# -*- coding: UTF-8 -*-
from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from importlib import import_module

user_app, user_model = settings.AUTH_ABSTRACT_USER_MODEL.split('.')
GenericUser = apps.get_app_config(user_app).get_model(user_model)
cmodels = import_module("apps.{}.models".format(settings.COMMON_APP))


class ScaplRole(models.Model):
    """ This model defines possible roles for users in relationship with the DataSequence model """
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(GenericUser, null=True, blank=True, related_name="created_roles")
    name = models.CharField(max_length=120)
    description = models.TextField(null=True)
    date_created = models.DateTimeField(verbose_name=_(u'Creation date'), auto_now_add=True, auto_now=False, editable=False)
    date_modified = models.DateTimeField(verbose_name=_(u'Last modification date'), auto_now_add=False, auto_now=True, editable=False)
    scope = models.IntegerField(choices=((0, "All users", ), (1, "Only normal users", ), (2, "Only security users", ), ), default=0)

    class Meta:
        verbose_name = _("User role")
        verbose_name_plural = _("User roles")

    def __str__(self):
        return self.name


class NormalUserManager(cmodels.GenericUserManager):
    def get_queryset(self):
        return super(NormalUserManager, self).get_queryset().filter(type=0)


class SecurityUserManager(cmodels.GenericUserManager):
    def get_queryset(self):
        return super(SecurityUserManager, self).get_queryset().filter(type=1)


class ScaplUser(GenericUser):
    type = models.IntegerField(choices=((0, _("Normal user"), ), (1, _("Security user"), )), default=0)
    role = models.ForeignKey(ScaplRole, related_name="scapl_users", blank=True, null=True)


class NormalUser(ScaplUser):
    """ This model defines a normal user for the wizard application """
    objects = NormalUserManager()

    class Meta:
        proxy = True
        verbose_name = _("Normal user")
        verbose_name_plural = _("Normal users")

    def save(self, *args, **kwargs):
        self.type = 0
        return super(NormalUser, self).save(*args, **kwargs)


class SecurityUser(ScaplUser):
    """ This model defines a normal user for the wizard application """
    objects = SecurityUserManager()

    class Meta:
        proxy = True
        verbose_name = _("Security user")
        verbose_name_plural = _("Security users")

    def save(self, *args, **kwargs):
        self.type = 1
        return super(SecurityUser, self).save(*args, **kwargs)
