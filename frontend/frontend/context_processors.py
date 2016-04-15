# -*- coding: UTF-8 -*-
from django.conf import settings


def project_name(request):
    return {'PROJECT_NAME': settings.PROJECT_NAME, 'PROJECT_AUTHORS': settings.PROJECT_AUTHORS}
