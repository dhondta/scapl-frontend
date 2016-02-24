# -*- coding: UTF-8 -*-
from django.apps import apps
from django.conf import settings
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from .models import APLTask

scheme_tokens = settings.SCHEME_SOURCE.split('.')
scheme_app, scheme_views, scheme_func = ".".join(scheme_tokens[:-1]), scheme_tokens[-2], scheme_tokens[-1]
get_scheme = getattr(__import__(scheme_app, fromlist=[scheme_views]), scheme_func)


def start_wizard(request, apl_id=None, seq_id=None):
    if seq_id is None:
        return
    request.scheme = get_scheme(seq_id)
    print(request.scheme)
    return
    #return load_apl_task(request, apl_id) if apl_id else create_apl_task(request)


def create_apl_task(request):
    return render(request)


def load_apl_task(request, apl_id):
    return render(request)


def trigger_data_item(*args, **kwargs):
    pass
