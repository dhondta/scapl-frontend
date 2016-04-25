# -*- coding: UTF-8 -*-
from .models import Tooltip


def tooltips(request):
    """ Inspired from: https://github.com/svdgraaf/django-tooltips,
        Modified to handle base URL (and not strict URL) """
    return {'tooltips': Tooltip.objects.filter(base_url__startswith=request.path)}
