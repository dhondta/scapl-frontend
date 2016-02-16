# -*- coding: UTF-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SchemeAppConfig(AppConfig):
    name = 'apps.scheme'
    verbose_name = _("1- Wizard Scheme Design")


class CommonAppConfig(AppConfig):
    name = 'apps.common'
    verbose_name = _("2- General Information")


class ProfilesAppConfig(AppConfig):
    name = 'apps.profiles'
    verbose_name = _("3- User Profile Information")


class WizardAppConfig(AppConfig):
    name = 'apps.wizard'
    verbose_name = _("4- Wizard Tasks")


class CeleryAppConfig(AppConfig):
    name = 'djcelery'
    verbose_name = _("5- Asynchronous Background Tasks")
