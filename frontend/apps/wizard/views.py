# -*- coding: UTF-8 -*-
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from .forms import TaskInitStepForm, TaskSequenceSelectionForm
from .models import Report, Task, TaskItem
from .search import get_query
from .utils import make_datatable, make_wizard


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


def start_wizard(request, apl_id=None, seq_id=None):

    def allowed_apl(sr, a):
        if isinstance(a, int):
            a = Task.objects.get(id=a)
        if request.user.pk not in [a.author.pk] + [x.pk for x in a.contributors.all()]:
            messages.add_message(sr, messages.ERROR, _('You are not allowed to edit this task'))
            return False
        return True

    def allowed_sequence(sr, s):
        if s not in [x.pk for x in request.user.role.related_sequences.all()]:
            messages.add_message(request, messages.ERROR, _('You are not allowed to run this wizard'))
            return False
        return True

    def create_apl(subrequest):
        form = TaskInitStepForm(data=subrequest.POST)
        if form.is_valid():
            apl = form.save(request=subrequest)
            subrequest.session['apl'] = [apl.id, apl.reference]
            messages.add_message(subrequest, messages.SUCCESS, _('New APL task created'))
        else:
            try:
                apl = Task.objects.get(keywords=form.data['keywords'])
                messages.add_message(subrequest, messages.WARNING, _('APL task already exists'))
                if not allowed_apl(subrequest, apl):
                    return redirect('tasks')
                subrequest.session['apl'] = [apl.id, apl.reference]
            except (KeyError, Task.DoesNotExist):
                pass
        return start_wizard(subrequest) if subrequest.session.get('apl') is not None \
            else render(subrequest, 'wizard/wizard.html', {'create_form': form})

    def select_sequence(subrequest):
        form, sequences = None, subrequest.user.role.related_sequences.all()
        if len(sequences) == 0:
            messages.add_message(subrequest, messages.ERROR, _("You don't have any sequence associated yet, please contact your administrator."))
            return redirect('home')
        elif len(sequences) == 1:
            subrequest.session['sequence'] = [sequences[0].id, sequences[0].name]
        else:
            form = TaskSequenceSelectionForm(data=subrequest.POST, choices=sequences)
            if form.is_valid():
                seq_id = int(form.cleaned_data['sequence'])
                if not allowed_sequence(subrequest, seq_id):
                    return redirect('tasks')
                sequence = sequences[seq_id]
                subrequest.session['sequence'] = [sequence.id, sequence.name]
        return start_wizard(subrequest) if subrequest.session.get('sequence') is not None \
            else render(subrequest, 'wizard/wizard.html', {'select_form': form})

    # if ID's are given in GET parameters, then ensure not in creation mode, check if user is authorized to edit this task
    #  and load the task if relevant
    if apl_id and seq_id:
        apl_id, seq_id = int(apl_id), int(seq_id)
        if not allowed_apl(request, apl_id) or not allowed_sequence(request, seq_id):
            return redirect('tasks')
        for pending in request.session['pending']:
            if pending['apl_id'] == apl_id:
                break
        # put the pending task at the end of the 'pending' list
        request.session['pending'].remove(pending)
        request.session['pending'].append(pending)
        current = (apl_id, seq_id, )
    # otherwise, create a new task
    else:
        # ensure that required fields are present
        request.session.setdefault('pending', [])
        apl, seq = request.session.get('apl'), request.session.get('sequence')
        # if no currently selected APL, create one
        if apl is None:
            return create_apl(request)
        # if no currently selected data sequence, select one (or if only one for the current user, immediately return seq_id)
        if seq is None:
            return select_sequence(request)
        # then set 'creation' flag to False, update the current APL data and update pending tasks list
        if apl[0] not in [x['apl_id'] for x in request.session['pending']]:
            request.session['pending'].append({'apl_id': apl[0], 'seq_id': seq[0], 'reference': apl[1], 'sequence': seq[1]})
        while len(request.session['pending']) > 3:
            request.session['pending'].pop(0)
        current = (request.session['apl'][0], request.session['sequence'][0], )
        request.session['apl'] = None
        request.session['sequence'] = None
    return render(request, 'wizard/wizard.html', {'wizard': make_wizard(*current)})


def save_data_item(request):
    if request.method == 'POST':
        apl, item_id = Task.objects.get(id=int(request.POST['apl'])), int(request.POST['item'])
        if apl.author == request.user or request.user in apl.contributors.all():
            try:
                di = TaskItem.objects.get(apl=apl, item_id=item_id)
            except TaskItem.DoesNotExist:
                di = TaskItem(apl=apl, item_id=item_id)
            value = request.POST['value']
            if value.strip() != '<br>':
                # TODO: implement HTML filtering and/or checking before returning 'value' to the user
                value = mark_safe(value)
                di.value = value
                di.save()
                apl.save(update_fields=['date_modified'])
                return JsonResponse({'status': 200, 'value': value})
            return JsonResponse({'status': 400, 'error': _('Item save failed').__unicode__()})
        else:
            return JsonResponse({'status': 400, 'error': _('You are not allowed to edit this task').__unicode__()})
    return JsonResponse({'status': 400})
