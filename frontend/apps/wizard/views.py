# -*- coding: UTF-8 -*-
import re
from celery.result import AsyncResult
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.html import mark_safe
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_http_methods
from importlib import import_module
from kombu import Connection
from kombu.compat import Publisher, Consumer
from .forms import TaskInitStepForm, TaskSequenceSelectionForm
from .models import Report, Task, TaskItem
from .search import get_query
from .utils import make_datatable, make_wizard

smodels = import_module("apps.scheme.models")


@require_http_methods(["GET"])
def list_reports(request):
    table_title, order, headers, records = make_datatable('reports', Report.objects.all())
    return render(request, 'wizard/datatable.html', locals())


@require_http_methods(["GET"])
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
@require_http_methods(["POST"])
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
        if sr.user.pk not in [a.author.pk] + [x.pk for x in a.contributors.all()]:
            messages.add_message(sr, messages.ERROR, _('You are not allowed to edit this task'))
            return False
        return True

    def allowed_sequence(sr, s):
        if len(sr.user.role.related_sequences.filter(id=s)) == 0:
            messages.add_message(sr, messages.ERROR, _('You are not allowed to run this wizard'))
            return False
        return True

    def create_apl(sr):
        form = TaskInitStepForm(data=sr.POST)
        if form.is_valid():
            apl = form.save(request=sr)
            messages.add_message(sr, messages.SUCCESS, _('New APL task created'))
            sr.session['apl'] = [apl.id, apl.reference, True]
        else:
            try:
                apl = Task.objects.get(keywords=form.data['keywords'])
                messages.add_message(sr, messages.WARNING, _('APL task already exists'))
                if not allowed_apl(sr, apl):
                    return redirect('tasks')
                sr.session['apl'] = [apl.id, apl.reference, True]
            except (KeyError, Task.DoesNotExist):
                pass
        return start_wizard(sr) if sr.session.get('apl') is not None else render(sr, 'wizard/wizard.html', {'create_form': form})

    def select_sequence(sr):
        form, sequences = None, sr.user.role.related_sequences.all()
        if len(sequences) == 0:
            messages.add_message(sr, messages.ERROR, _("You don't have any sequence associated yet, please contact your administrator."))
            return redirect('home')
        elif len(sequences) == 1:
            sr.session['sequence'] = [sequences[0].id, sequences[0].name]
        else:
            form = TaskSequenceSelectionForm(data=sr.POST, choices=sequences)
            if form.is_valid():
                seq_id = int(form.cleaned_data['sequence'])
                if not allowed_sequence(sr, seq_id):
                    return redirect('tasks')
                sequence = sequences[seq_id]
                sr.session['sequence'] = [sequence.id, sequence.name]
        return start_wizard(sr) if sr.session.get('sequence') is not None else render(sr, 'wizard/wizard.html', {'select_form': form})

    # if ID's are given in GET parameters, then ensure not in creation mode, check if user is authorized to edit this task
    #  and load the task if relevant
    if apl_id and seq_id:
        apl_id, seq_id, recent = int(apl_id), int(seq_id), None
        current = (apl_id, seq_id, )
        edit = not allowed_apl(request, apl_id) or not allowed_sequence(request, seq_id)
        # check if selected task is in the recent ones
        for recent in request.session['recent']:
            if recent['id'][0] == apl_id:
                break
        # if not, try to load the selected task with the given sequence
        if not recent:
            apl = Task.objects.get(id=apl_id)
            if not allowed_sequence(request, seq_id):
                return redirect('tasks')
            seq = request.user.role.related_sequences.filter(id=seq_id)
            recent = {'id': current, 'reference': apl.reference, 'sequence': seq[0].name}
        else:
            request.session['recent'].remove(recent)
        # put the recent task at the end of the 'recent' list
        request.session['recent'].append(recent)
    else:
        # test if apl_id exists (occurs when coming from an anchor in the tasks list (NB: no sequence selected yet)
        if apl_id:
            apl = Task.objects.get(id=int(apl_id))
            request.session['apl'] = [apl.id, apl.reference, allowed_apl(request, apl)]
        # ensure that required fields are present
        request.session.setdefault('recent', [])
        apl, seq = request.session.get('apl'), request.session.get('sequence')
        # if no currently selected APL, create one
        if apl is None:
            return create_apl(request)
        # if no currently selected data sequence, select one (or if only one for the current user, immediately return seq_id)
        if seq is None:
            return select_sequence(request)
        current, edit = (apl[0], seq[0], ), apl[2]
        # then set 'creation' flag to False, update the current APL data and update recent tasks list
        if apl[0] not in [x['id'][0] for x in request.session['recent']]:
            request.session['recent'].append({'id': current, 'reference': apl[1], 'sequence': seq[1]})
        while len(request.session['recent']) > settings.MAX_RECENT_TASKS:
            request.session['recent'].pop(0)
        request.session['apl'] = None
        request.session['sequence'] = None
    return render(request, 'wizard/wizard.html', {'wizard': make_wizard(*current), 'edit_mode': edit})


@require_http_methods(["POST"])
def save_data_item(request):
    apl, item_id = Task.objects.get(id=int(request.POST['apl'])), int(request.POST['item'])
    if apl.author == request.user or request.user in apl.contributors.all():
        try:
            di = TaskItem.objects.get(apl=apl, item_id=item_id)
        except TaskItem.DoesNotExist:
            di = TaskItem(apl=apl, item_id=item_id)
        value = request.POST['value']
        if not re.sub(r'^\<p\>', '', re.sub(r'\<\/p\>$', '', value)) in ['', '<br>']:
            # TODO: implement HTML filtering and/or checking before returning 'value' to the user
            sanitized_value = mark_safe(value)
            di.value = sanitized_value
            di.save()
            apl.save(update_fields=['date_modified'])
            return JsonResponse({'status': 200, 'value': sanitized_value})
        return JsonResponse({'status': 400, 'error': _('Item save failed').__unicode__()})
    else:
        return JsonResponse({'status': 400, 'error': _('You are not allowed to edit this task').__unicode__()})


@require_http_methods(["POST"])
def trigger_data_item(request, task_id=None):

    def send_as_task(task, task_id, args=(), kwargs={}, routing='default', retries=0):
        with Connection(settings.BROKER_URL) as conn:
            with Publisher(connection=conn, exchange="scapl", exchange_type="topic",
                           routing_key=settings.ROUTING_KEYS[routing]) as pub:
                payload = {
                    'task': task,
                    'id': task_id,
                    'args': args,
                    "kwargs": kwargs,
                    "retries": retries,
                    "eta": str(now()),
                }
                pub.send(payload)

    # if no task_id provided, trigger the data item
    args, kwargs = (), {}
    if task_id is None:
        apl_id, item_id = int(request.POST['apl']), int(request.POST['item'])
        apl = Task.objects.get(id=apl_id)
        di = smodels.DataItem.objects.get(id=item_id)
        if isinstance(di, smodels.SEDataItem):
            routing = 'search'
            args = ('Scapl', di.api, )
            kwargs = {'keywords': di.keywords, 'suggestions': di.max_suggestions}
        elif isinstance(di, smodels.SEDataItem):
            routing = 'automation'
            args = ('Scapl', di.call, )
        else:
            return JsonResponse({'status': 200, 'result': None})
        task = '{}-{}'.format(repr(apl), repr(di))
        task_id = '{}-{}'.format(apl_id, item_id)
        send_as_task(task, task_id, args, kwargs, routing=routing)
        return JsonResponse({'status': 200, 'result': task_id})
    # otherwise, ask for result of the designated task
    else:
        task = AsyncResult(task_id)
        result = task.get() if task.status == 'SUCCESS' else None
        return JsonResponse({'status': 200, 'task_status': task.status, 'result': result})
