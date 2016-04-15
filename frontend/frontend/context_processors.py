# -*- coding: UTF-8 -*-
from django.conf import settings


def project_info(request):
    return {
        'PROJECT_NAME': settings.PROJECT_NAME,
        'PROJECT_AUTHORS': settings.PROJECT_AUTHORS,
    }


def layout_parameters(request):
    return {
        'ITEM_EDITION_HEIGHT': settings.SUMMERNOTE_CONFIG['height'],
    }
