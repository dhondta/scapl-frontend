# -*- coding: UTF-8 -*-
from django.utils.safestring import mark_safe
from importlib import import_module
from .datatables import reports_template, tasks_template
from .forms import TaskItemForm
from .models import Task, TaskItem

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
    scheme = get_scheme(seq_id)
    apl = Task.objects.get(id=apl_id)
    saved_di = TaskItem.objects.filter(apl=apl)
    ds, seq = scheme.items()[0]
    wizard = {'reference': apl.reference, 'title': ds.name, 'help': ds.description, 'steps': []}
    for dl, lst in seq.items():
        step = {'title': dl.name, 'help': dl.description, 'items': []}
        for di in lst:
            item_id = di.id
            try:
                form = TaskItemForm(instance=saved_di.filter(item_id=di.id)[0])
            # occurs when 'filter' method returns an empty queryset ('[0]' then causes this error)
            except IndexError:
                form = TaskItemForm()
            # Summernote is used as a textarea editor ; as its JS uses variable names depending on 'id',
            #  this has to start with characters and not digits (that's why 'di' is used as a prefix)
            form.fields['value'].widget.attrs['id'] = "di{}".format(item_id)
            item = {
                'id': item_id,
                'label': di.name,
                'help': di.description,
                'form': form,
                'is_auto': not isinstance(di, smodels.ManualDataItem),
            }
            step['items'].append(item)
        wizard['steps'].append(step)
    return wizard
