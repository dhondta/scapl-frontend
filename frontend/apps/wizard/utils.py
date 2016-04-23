# -*- coding: UTF-8 -*-
from django.conf import settings
from django.utils.safestring import mark_safe
from frontend import celery_app
from importlib import import_module
from kombu import Connection
from .datatables import reports_template, tasks_template
from .forms import TaskItemForm, SAMPLE_KEYWORDS
from .models import Task, TaskItem, TaskItemResult
from .signals import wizard_load

get_scheme = getattr(__import__("apps.scheme.utils", fromlist=['utils']), 'get_scheme')
smodels = import_module("apps.scheme.models")


def make_datatable(template_name, objects, exclude_field=None):
    """ This function makes a valid Datatables from a template dictionary using objects (that is, instances of a model),
     discarding invalid fields
    :param template_name: the template dictionary to use to build the table
    :param objects: list of instances of a model
    :param exclude_fields: list of fields to be excluded (aimed to discard badly formatted fields
    :return: a triple (title, order of columns, list of records)
    """
    headers, records = [], []
    # the following lambda lazily triggers the evaluation of item 'i' handling an input object if specified
    evaluate = lambda i, o=None: (i(o) if o else i()) if isinstance(i, type(lambda: None)) else i
    # retrieve template
    try:
        template = globals()['{}_template'.format(template_name)]
    except NameError:
        return 'Undefined', [], [], []
    # drop excluded field
    if exclude_field:
        template['fields'].pop(exclude_field, None)
        template['order'].remove(exclude_field)
    # prepare the header according to the provided order
    for field in template['order']:
        headers.append(template['fields'][field]['header'])
    # now prepare the list of records
    for obj in objects:
        record = {}
        for field in template['fields'].keys():
            try:
                field_obj = template['fields'][field]
                value = evaluate(field_obj['value'], obj)
                # now, other keywords can be handled
                if 'url' in field_obj.keys():
                    value = '<a href="{}">{}</a>'.format(evaluate(field_obj['url'], obj), value)
                # finally, save the handled value in the record
                record[field] = mark_safe(value)
            except:
                return make_datatable(template_name, objects, field)
        records.append(record)
    return template['title'], template['order'], headers, records


def make_wizard(apl_id, seq_id):
    """ This function makes a wizard from the data scheme defined with the application 'scheme' using the utility function 'get_scheme'
    :param apl_id: APL identifying number
    :param seq_id: sequence identifying number
    :return: a wizard dictionary containing its structure, help texts, ...
    """

    def trigger_item(apl, ti, di):
        task = TaskItemResult(task=ti)
        task.save()
        # check if signal is to be sent in order to trigger automated data items
        if isinstance(di, smodels.SEDataItem):
            keywords = [y for x, y in SAMPLE_KEYWORDS][[x for x, y in SAMPLE_KEYWORDS].index(apl.keywords)]
            if di.keywords not in [None, 'None', 'null']:
                keywords = ','.join([keywords, di.keywords])
            cmd = di.api.format(keywords=keywords, suggestions=di.max_suggestions)
            sigresult = wizard_load.send(None, task_id=repr(ti), cmd=cmd, conn=conn, routing='search')
            return sigresult[0][1], True
        elif isinstance(di, smodels.ASDataItem):
            cmd = di.call.format(packages=apl.packages)
            sigresult = wizard_load.send(None, task_id=repr(ti), cmd=cmd, conn=conn, routing='automation')
            return sigresult[0][1], False
        else:
            return None, False

    # first, get the data scheme
    scheme = get_scheme(seq_id)
    # then, get the related APL with its list of already saved items
    apl = Task.objects.get(id=apl_id)
    saved_di = TaskItem.objects.filter(apl=apl)
    # now, prepare the wizard, triggering asynchronous tasks for each data item in the background
    ds, seq = scheme.items()[0]
    wizard = {'reference': apl.reference, 'title': ds.name, 'help': ds.description, 'steps': [], 'errors': []}
    with Connection(settings.BROKER_URL) as conn:
        for dl, lst in seq.items():
            step = {'title': dl.name, 'help': dl.description, 'items': []}
            for di in lst:
                # if a saved data item exists for this particular item, fill in the form
                try:
                    current_item = saved_di.filter(item_id=di.id)[0]
                    form = TaskItemForm(instance=current_item)
                # otherwise, create an emtpy form for the data item
                except IndexError:
                    current_item = TaskItem(apl=apl, item=di)
                    current_item.save()
                    form = TaskItemForm(instance=current_item)
                # Summernote is used as a textarea editor ; as its JS uses variable names depending on 'id',
                #  this has to start with characters and not digits (that's why 'di' is used as a prefix)
                form.fields['value'].widget.attrs['id'] = "di{}".format(di.id)
                # at this point, check if the data item is automated and if an asynchronous task record exists
                #  if not, trigger a new asynchronous task and record it
                is_auto = not isinstance(di, smodels.ManualDataItem)
                error, refresh, result, task_id = 4 * [None]
                if is_auto:
                    task_id = repr(current_item)
                    # if it exists, retrieve the AsyncResult
                    if TaskItemResult.objects.filter(task=current_item).exists():
                        task = celery_app.AsyncResult(task_id)
                        result = task.get() if task.status == 'SUCCESS' else None
                        refresh = isinstance(di, smodels.SEDataItem)
                    # if not, create a new record and trigger the task
                    else:
                        error, refresh = trigger_item(apl, current_item, di)
                item = {
                    'id': di.id,
                    'task': task_id,
                    'label': di.name,
                    'help': di.description,
                    'form': form,
                    'is_auto': is_auto,
                    'refresh': refresh,
                    'result': result,
                }
                step['items'].append(item)
                if error is not None:
                    wizard['errors'].append(error)
            wizard['steps'].append(step)
    return wizard
