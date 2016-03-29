# -*- coding: UTF-8 -*-
from django.conf import settings
from .forms import APLTaskItemForm
from .models import APLTaskItem

get_scheme = getattr(__import__("{}.utils".format(settings.SCHEME_SOURCE), fromlist=['utils']), 'get_scheme')


def make_form(apl_id, seq_id):
    scheme = get_scheme(seq_id)
    saved_di = APLTaskItem.objects.filter(id=apl_id)
    ds, seq = scheme.items()[0]
    wizard = {'title': ds.name, 'help': ds.description, 'steps': []}
    for dl, lst in seq.items():
        step = {'title': dl.name, 'help': dl.description, 'items': []}
        for di in lst:
            item_id = di.id
            try:
                form = APLTaskItemForm(instance=saved_di.filter(item_id=di.id)[0])
            # occurs when 'filter' method returns an empty queryset ('[0]' then causes this error)
            except IndexError:
                form = APLTaskItemForm()
            form.fields['value'].widget.attrs['id'] = item_id
            item = {'label': di.name, 'help': di.description, 'id': item_id, 'form': form}
            step['items'].append(item)
        wizard['steps'].append(step)
    return wizard
