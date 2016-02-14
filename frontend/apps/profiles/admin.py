# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib import admin
from importlib import import_module
from .models import NormalUser, SecurityUser

cadmin = import_module("apps.{}.admin".format(settings.COMMON_APP))


admin.site.register(NormalUser, cadmin.GenericUserAdmin)
admin.site.register(SecurityUser, cadmin.GenericUserAdmin)
