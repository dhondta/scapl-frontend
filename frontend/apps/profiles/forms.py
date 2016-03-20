# -*- coding: UTF-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from .models import NormalUser, SecurityUser

cforms = import_module("apps.{}.forms".format(settings.COMMON_APP))


class NormalUserUpdateForm(cforms.GenericUserUpdateForm):
    class Meta(cforms.GenericUserUpdateForm.Meta):
        model = NormalUser

    def __init__(self, *args, **kwargs):
        super(NormalUserUpdateForm, self).__init__(*args, **kwargs)
#    pass
#NormalUserUpdateForm.Meta.model = NormalUser


class NormalUserForm(cforms.GenericUserForm):
    class Meta(cforms.GenericUserForm.Meta):
        model = NormalUser

    def __init__(self, *args, **kwargs):
        super(NormalUserForm, self).__init__(*args, **kwargs)
#NormalUserForm.Meta.model = NormalUser


class SecurityUserUpdateForm(cforms.GenericUserUpdateForm):
    class Meta(cforms.GenericUserUpdateForm.Meta):
        model = SecurityUser
#SecurityUserUpdateForm.Meta.model = SecurityUser


class SecurityUserForm(cforms.GenericUserForm):
    class Meta(cforms.GenericUserForm.Meta):
        model = SecurityUser
# SecurityUserForm.Meta.model = SecurityUser
