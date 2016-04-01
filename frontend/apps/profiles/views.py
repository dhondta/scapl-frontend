# -*- coding: UTF-8 -*-
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from importlib import import_module
from .forms import ScaplUserCreationForm, ScaplUserUpdateForm

cviews = import_module("apps.common.views")


@login_required
def home(request):
    return render(request, 'profiles/home.html')


@login_required
def profile(request):
    if request.method == 'POST':
        form = ScaplUserUpdateForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.instance)
    else:
        form = ScaplUserUpdateForm(instance=request.user)
    return render(request, 'profiles/edit.html', {'form': form})


@login_required
def reports(request):
    return render(request, 'profiles/reports.html')


def password(request):
    return render(request, 'profiles/forgot-password.html')


signin = cviews.signin('common/index.html')


signout = cviews.signout()


signup = cviews.signup(ScaplUserCreationForm, 'profiles/signup.html')
