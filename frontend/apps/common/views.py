# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _
from .forms import GenericUserCreationForm

default_theme = 'default'
if hasattr(settings, 'DEFAULT_BOOTSTRAP_THEME'):
    default_theme = settings.DEFAULT_BOOTSTRAP_THEME


def signin(template='index.html', home_view='home'):
    def signin_template(request):
        next = request.GET.get('next')
        if request.user.is_authenticated():
            return redirect(next or home_view)
        if request.method == 'POST':
            user = authenticate(email=request.POST['email'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    msg = _("Successfully signed in")
                    if not msg in [m.message for m in messages.get_messages(request)]:
                        messages.add_message(request, messages.SUCCESS, msg)
                    return redirect(next or home_view)
                else:
                    messages.add_message(request, messages.ERROR, _("Disabled account"))
            else:
                messages.add_message(request, messages.ERROR, _("Bad credentials"))
        return render(request, template, {'theme': default_theme})
    return signin_template


def signout(redirect_view='signin'):
    def signout_template(request):
        if request.user.is_authenticated():
            logout(request)
        return redirect(redirect_view)
    return signout_template


def signup(form_class=GenericUserCreationForm, template='signup.html', home_view='home', index_view='index'):
    def signup_template(request):
        if request.user.is_authenticated():
            return redirect(home_view)
        form = form_class(data=request.POST)
        if form.is_valid():
            user = form.save()
            messages.add_message(request, messages.SUCCESS, _("Successfully signed up"))
            if user.type == 0:
                user = authenticate(email=request.POST['email'], password=request.POST['password'])
                if user is not None:
                    login(request, user)
                    return redirect(home_view)
            else:
                messages.add_message(request, messages.WARNING, _("Administrator will activate your account as soon as possible"))
                return redirect(index_view)
        return render(request, template, {'form': form})
    return signup_template


def signin_or_signup(template='index.html', form_class=GenericUserCreationForm, home_view='home', index_view='index'):
    def signin_or_signup_template(request):
        next = request.GET.get('next')
        if request.user.is_authenticated():
            return redirect(next or home_view)
        form = form_class()
        if request.method == 'POST':
            if request.POST['type'] == 'signin':
                user = authenticate(email=request.POST['email'], password=request.POST['password'])
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        msg = _("Successfully signed in")
                        if not msg in [m.message for m in messages.get_messages(request)]:
                            messages.add_message(request, messages.SUCCESS, msg)
                        return redirect(next or home_view)
                    else:
                        messages.add_message(request, messages.ERROR, _("Disabled account"))
                else:
                    messages.add_message(request, messages.ERROR, _("Bad credentials"))
            elif request.POST['type'] == 'signup':
                form = form_class(data=request.POST)
                if form.is_valid():
                    user = form.save()
                    messages.add_message(request, messages.SUCCESS, _("Successfully signed up"))
                    if user.type == 0:
                        user = authenticate(email=request.POST['email'], password=request.POST['password'])
                        if user is not None:
                            login(request, user)
                            return redirect(home_view)
                    else:
                        messages.add_message(request, messages.WARNING, _("Administrator will activate your account as soon as possible"))
                        return redirect(index_view)
        return render(request, template, {'theme': default_theme, 'form': form})
    return signin_or_signup_template
