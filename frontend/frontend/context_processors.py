# -*- coding: UTF-8 -*-
from django.conf import settings


def project_info(request):
    return {
        'PROJECT_NAME': settings.PROJECT_NAME,
        'PROJECT_AUTHORS': settings.PROJECT_AUTHORS,
    }


def async_task_parameters(request):
    return {
        'RESULT_REFRESH_DELAY': settings.RESULT_REFRESH_DELAY,
    }
