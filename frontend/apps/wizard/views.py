# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from .forms import APLTaskInitStepForm, APLTaskSequenceSelectionForm
from .models import APLTask, APLTaskItem
from .utils import make_form


def create_apl(request):
    form = APLTaskInitStepForm(data=request.POST)
    if form.is_valid():
        request.session['apl'] = form.save(request=request)
    else:
        try:
            request.session['apl'] = APLTask.objects.get(keywords=form.data['keywords']).id
        except (KeyError, APLTask.DoesNotExist):
            pass
    return start_wizard(request) if request.session.get('apl') is not None \
        else render(request, 'wizard/create.html', {'form': form})


def select_sequence(request):
    form, sequences = None, request.user.role.related_sequences.all()
    if len(sequences) == 0:
        request.message = _("You don't have any sequence associated yet, please contact your administrator.")
    elif len(sequences) == 1:
        request.session['sequence'] = sequences[0].id
    else:
        form = APLTaskSequenceSelectionForm(data=request.POST, choices=sequences)
        if form.is_valid():
            request.session['sequence'] = sequences[int(form.cleaned_data['sequence'])].id
    return start_wizard(request) if request.session.get('sequence') is not None \
        else render(request, 'wizard/select.html', {'form': form})


@login_required
def start_wizard(request):
    # administrators (type 2) are not aimed to handle APL's
    if request.user.type == 2:
        return redirect('home')
    apl_id, seq_id = request.session.get('apl'), request.session.get('sequence')
    if apl_id is None:
        return create_apl(request)
    if seq_id is None:
        return select_sequence(request)
#    del request.session['apl'], request.session['sequence']
    print({'wizard': make_form(apl_id, seq_id)})
    return render(request, 'wizard/wizard.html', {'wizard': make_form(apl_id, seq_id)})


@login_required
def save_data_item(request):
    if request.method == 'POST':
        apl_id, item_id, user_id = int(request.POST['apl']), int(request.POST['item']), request.user.id
        apl = APLTask.objects.get(id=apl_id)
        if apl.author.id == user_id or user_id in [x.id for x in apl.contributors.all()]:
            try:
                di = APLTaskItem.objects.get(apl=apl, item_id=item_id)
            except APLTaskItem.DoesNotExist:
                di = APLTaskItem(apl=apl, item_id=item_id)
            di.value = request.POST['value']
            di.save()
    return HttpResponse('')
