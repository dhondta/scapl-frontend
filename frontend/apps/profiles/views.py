# -*- coding: UTF-8 -*-
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from .forms import ScaplUserCreationForm, ScaplUserUpdateForm

cviews = import_module("apps.common.views")


def home(request):
    return render(request, 'profiles/home.html')


def profile(request):
    if request.method == 'POST':
        # this hack is necessary because of the disabled 'email' field that is not passed through POST data
        POST = request.POST.copy()
        POST['email'] = request.user.email
        form = ScaplUserUpdateForm(data=POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            if not user.check_password(form.cleaned_data['old_password']):
                messages.add_message(request, messages.SUCCESS, _('Password successfully changed'))
            messages.add_message(request, messages.SUCCESS, _('Profile data successfully updated'))
            return redirect('profile')
        else:
            messages.add_message(request, messages.ERROR, _('Profile data update failed'))
            for field, error in form.errors.items():
                messages.add_message(request, messages.ERROR, '{}: {}'.format(field.replace('_', ' ').capitalize(), '\n'.join(error)))
    else:
        form = ScaplUserUpdateForm(instance=request.user)
    return render(request, 'profiles/edit.html', {'form': form})


def password(request):
    return render(request, 'profiles/forgot-password.html')


signin_or_signup = cviews.signin_or_signup('common/index.html', ScaplUserCreationForm)


signout = cviews.signout('index')
