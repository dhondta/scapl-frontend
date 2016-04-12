# -*- coding: UTF-8 -*-
from django.utils.safestring import mark_safe
from .datatables import reports_template, tasks_template
from .forms import TaskItemForm
from .models import Task, TaskItem

get_scheme = getattr(__import__("apps.scheme.utils", fromlist=['utils']), 'get_scheme')


def make_datatable(template_name, objects, exclude_fields=[]):
    headers, records = [], []
    try:
        template = globals()['{}_template'.format(template_name)]
    except NameError:
        return 'Undefined', [], [], []
    for field in exclude_fields:
        template['fields'].pop(field, None)
    for field in template['order']:
        headers.append(template['fields'][field]['header'])
    for obj in objects:
        record = {}
        for field in template['fields'].keys():
            try:
                value = template['fields'][field]['value']
                # the following lazily triggers the evaluation of field['value'] (that could refer to 'obj')
                record[field] = mark_safe(value(obj) if isinstance(value, type(lambda: None)) else value)
            except:
                exclude_fields.append(field)
                return make_datatable(template_name, objects, exclude_fields)
        records.append(record)
    return template['title'], template['order'], headers, records


def make_wizard(apl_id, seq_id):
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
            item = {'label': di.name, 'help': di.description, 'id': item_id, 'form': form}
            step['items'].append(item)
        wizard['steps'].append(step)
    return wizard
