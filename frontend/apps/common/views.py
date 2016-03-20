# -*- coding: UTF-8 -*-
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')

def registration(request):
    return render(request, 'registration.html')

def profile(request):
    return render(request, 'profile.html')

def home(request):
    return render(request, 'base.html')

