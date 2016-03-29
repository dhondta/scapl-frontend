# -*- coding: UTF-8 -*-
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import GenericUserCreationForm


def signin(template='index.html'):
    def signin_template(request):
        next = request.GET.get('next')
        if request.user.is_authenticated():
            return redirect(next or 'home')
        if request.method == 'POST':
            user = authenticate(email=request.POST['email'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(next or 'home')
                else:
                    request.message = "Disabled account"
            else:
                request.message = "Bad credentials"
        return render(request, template)
    return signin_template


def signout(redirect_view='signin'):
    def signout_template(request):
        if request.user.is_authenticated():
            logout(request)
        return redirect(redirect_view)
    return signout_template


def signup(form_class=GenericUserCreationForm, template='signup.html', home_view='home'):
    def signup_template(request):
        if request.user.is_authenticated():
            return redirect(home_view)
        form = form_class(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        return render(request, template, {'form': form})
    return signup_template
