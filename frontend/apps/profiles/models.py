# -*- coding: UTF-8 -*-
from django.apps import apps
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

user_app, user_model = settings.AUTH_USER_MODEL.split('.')
GenericUser = apps.get_app_config(user_app).get_model(user_model)


class NormalUser(GenericUser):
    """ This model defines a normal user for the wizard application """
    is_active = True

    class Meta:
        verbose_name = _("Normal user")
        verbose_name_plural = _("Normal users")


class SecurityUser(GenericUser):
    """ This model defines a normal user for the wizard application """

    class Meta:
        verbose_name = _("Security user")
        verbose_name_plural = _("Security users")
