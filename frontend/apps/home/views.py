# -*- coding: UTF-8 -*-
from django.template.loader import get_template
from django.shortcuts import render
from django.template import Context
from django.http import HttpResponse


def index(request):
    t = get_template('index.html')
    html = t.render()
    return HttpResponse(html)

def home(request):
    t = get_template('base.html')
    html = t.render()
    return HttpResponse(html)

