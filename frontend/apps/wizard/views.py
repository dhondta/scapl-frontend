# -*- coding: UTF-8 -*-
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from .forms import TaskInitStepForm, TaskSequenceSelectionForm
from .models import Report, Task, TaskItem
from .search import get_query
from .utils import make_datatable, make_wizard


def create_apl(request):
    form = TaskInitStepForm(data=request.POST)
    if form.is_valid():
        request.session['apl'] = form.save(request=request).id
        messages.add_message(request, messages.SUCCESS, _('New APL task created'))
    else:
        try:
            request.session['apl'] = Task.objects.get(keywords=form.data['keywords']).id
            messages.add_message(request, messages.INFO, _('APL task already exists'))
        except (KeyError, Task.DoesNotExist):
            pass
    return start_wizard(request) if request.session.get('apl') is not None \
        else render(request, 'wizard/wizard.html', {'create_form': form})


def list_reports(request):
    table_title, order, headers, records = make_datatable('reports', Report.objects.all())
    return render(request, 'wizard/datatable.html', locals())


def list_tasks(request):
    table_title, order, headers, tmp_records = make_datatable('tasks', Task.objects.all())
    records = []
    short_name = request.user.get_short_name()
    for record in tmp_records:
        if short_name in [record['author']] + record['contributors'].split('<br>'):
            record['highlight'] = True
        records.append(record)
    return render(request, 'wizard/datatable.html', locals())


# inspired from: http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def search(request):
    if request.method == 'POST':
        found_entries, keywords = [], request.POST.get('q').strip()
        if keywords:
            # first, search on apl tasks
            #entry_query = get_query(keywords, ['value'])
            #found_entries.append(Task.objects.filter(entry_query))
            # then, search on data items
            entry_query = get_query(keywords, ['value'])
            found_entries.append(Task.objects.filter(item_set__in=TaskItem.objects.filter(entry_query)))
            return JsonResponse({'status': 200, 'results': list({e.reference for e in found_entries})})
        return JsonResponse({'status': 200, 'results': None})
    return JsonResponse({'status': 400})


def select_sequence(request):
    form, sequences = None, request.user.role.related_sequences.all()
    if len(sequences) == 0:
        request.message = _("You don't have any sequence associated yet, please contact your administrator.")
    elif len(sequences) == 1:
        request.session['sequence'] = sequences[0].id
    else:
        form = TaskSequenceSelectionForm(data=request.POST, choices=sequences)
        if form.is_valid():
            request.session['sequence'] = sequences[int(form.cleaned_data['sequence'])].id
    return start_wizard(request) if request.session.get('sequence') is not None \
        else render(request, 'wizard/wizard.html', {'select_form': form})


def start_wizard(request):
    request.session.setdefault('pending', {})
    request.session.setdefault('creation', False)
    apl_id, seq_id = request.session.get('apl'), request.session.get('sequence')
    # if a task is already pending, put it in sessin and release 'apl' and 'sequence'
    if apl_id is not None and seq_id is not None and not request.session['creation']:
        request.session['creation'] = True
        request.session['pending'][apl_id] = seq_id
        request.session['apl'] = None
        request.session['sequence'] = None
        apl_id, seq_id = None, None
    if apl_id is None:
        return create_apl(request)
    if seq_id is None:
        return select_sequence(request)
    request.session['creation'] = False
    request.session['current'] = (apl_id, seq_id, )
    return render(request, 'wizard/wizard.html', {'wizard': make_wizard(apl_id, seq_id)})


def save_data_item(request):
    if request.method == 'POST':
        apl, item_id = Task.objects.get(id=int(request.POST['apl'])), int(request.POST['item'])
        if apl.author == request.user or request.user in apl.contributors.all():
            try:
                di = TaskItem.objects.get(apl=apl, item_id=item_id)
            except TaskItem.DoesNotExist:
                di = TaskItem(apl=apl, item_id=item_id)
            value = request.POST['value']
            if value != '':
                di.value = request.POST['value']
                di.save()
                apl.save(update_fields=['date_modified'])
                return JsonResponse({'status': 200})
            return JsonResponse({'status': 400, 'error': _('Item save failed').__unicode__()})
        else:
            return JsonResponse({'status': 400, 'error': _('You are not allowed to edit this task').__unicode__()})
    return JsonResponse({'status': 400})
