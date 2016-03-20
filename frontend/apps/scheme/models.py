# -*- coding: UTF-8 -*-
import json
from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from importlib import import_module

user_app, user_model = settings.AUTH_USER_MODEL.split('.')
ScaplUser = apps.get_app_config(user_app).get_model(user_model)
cmodels = import_module("apps.{}.models".format(settings.COMMON_APP))

profile_app, profile_model = settings.AUTH_ROLE_MODEL.split('.')
ScaplRole = apps.get_app_config(profile_app).get_model(profile_model)

# for name, obj in inspect.getmembers(settings.PROFILE_APP):
#     if inspect.isclass(obj) and name.endswith("User"):
#         exec("{} = {}".format(name, obj))


""" (see SCAPL's SDD section 4.2 Data Dictionary for more details about the data scheme and models' meaning) """


class AdministratorManager(cmodels.GenericUserManager):
    def get_queryset(self):
        return super(AdministratorManager, self).get_queryset().filter(type=2)


class Administrator(ScaplUser):
    """ This model defines an administrator for the wizard application """
    objects = AdministratorManager()

    class Meta:
        proxy = True
        verbose_name = _("Administrator")
        verbose_name_plural = _("Administrators")

    def save(self, *args, **kwargs):
        self.type = 2
        self.is_staff = True
        return super(Administrator, self).save(*args, **kwargs)


class Entity(models.Model):
    """ This model defines the generic structure of a data entity """
    name = models.CharField(max_length=120)
    description = models.TextField(null=True)
    date_created = models.DateTimeField(verbose_name=_(u'Creation date'), auto_now_add=True, auto_now=False, editable=False)
    date_modified = models.DateTimeField(verbose_name=_(u'Last modification date'), auto_now_add=False, auto_now=True, editable=False)

    class Meta:
        unique_together = ('name', 'description', )
        abstract = True


class DataSequence(Entity):
    """ This model defines the structure of a data sequence """
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(ScaplUser, null=True, blank=True, related_name="created_sequences")
    roles = models.ManyToManyField(ScaplRole, through='SequenceRoleAssociations', related_name="sequences")
    # max_users = models.IntegerField(default=5)

    class Meta:
        ordering = ('id', )
        verbose_name = _("Data sequence")
        verbose_name_plural = _("Data sequences")

    def __str__(self):
        return u'DS{}'.format(str(self.id).zfill(settings.DS_ID_DIGITS))


class DataList(Entity):
    """ This model defines the structure of a data list """
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(ScaplUser, null=True, blank=True, related_name="created_lists")
    sequences = models.ManyToManyField(DataSequence, through='ListSequenceAssociations', related_name="lists")

    class Meta:
        ordering = ('id', )
        verbose_name = _("Data list")
        verbose_name_plural = _("Data lists")

    def __str__(self):
        return u'DL{}'.format(str(self.id).zfill(settings.DL_ID_DIGITS))


class DataItem(Entity):
    """ This model defines the generic structure of a data item """
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(ScaplUser, null=True, blank=True, related_name="created_items")
    lists = models.ManyToManyField(DataList, through='ItemListAssociations', related_name="items")

    class Meta:
        ordering = ('id', )

    def __str__(self):
        return u'DI{}'.format(str(self.id).zfill(settings.DI_ID_DIGITS))


class ManualDataItem(DataItem):
    """ This model defines a manual data item (not triggering any task) """
    class Meta:
        verbose_name = _("Data item (Manual)")
        verbose_name_plural = _("Data items (Manual)")

    def __repr__(self):
        return u'manual'


class ASDataItem(DataItem):
    """ This model defines the structure of a data item particularized to the Automation System """
    call = models.TextField()

    class Meta:
        verbose_name = _("Data item (Automation System)")
        verbose_name_plural = _("Data items (Automation System)")

    def __repr__(self):
        return u'{}'.format(self.call)


class SEDataItem(DataItem):
    """ This model defines the structure of a data item particularized to the Search Engine """
    max_suggestions = models.IntegerField(default=0)
    keywords = models.CharField(max_length=256)  # TODO: change it to JSONField (Django 1.9+ if used with PostgreSQL)
    api = models.TextField()

    class Meta:
        verbose_name = _("Data item (Search Engine)")
        verbose_name_plural = _("Data items (Search Engine)")

    def setkeywords(self, keywords):  # TODO: this is error-prone due to the field's length ; add a validation
        self.keywords = json.dumps(keywords)

    def getkeywords(self):
        return json.loads(self.keywords)

    def __repr__(self):
        return u'{} {} {}'.format(self.api, self.keywords, self.max_suggestions)


class ItemListAssociations(models.Model):
    item = models.ForeignKey(DataItem, on_delete=models.CASCADE)
    list = models.ForeignKey(DataList, on_delete=models.CASCADE)
    item_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ('item_order', )
        verbose_name = _("Item/List association")
        verbose_name_plural = _("Item/List associations")

    def __str__(self):
        return self.item.description


class ListSequenceAssociations(models.Model):
    list = models.ForeignKey(DataList, on_delete=models.CASCADE)
    sequence = models.ForeignKey(DataSequence, on_delete=models.CASCADE)
    list_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ('list_order', )
        verbose_name = _("List/Sequence association")
        verbose_name_plural = _("List/Sequence associations")

    def __str__(self):
        return self.list.description


class SequenceRoleAssociations(models.Model):
    sequence = models.ForeignKey(DataSequence, on_delete=models.CASCADE)
    role = models.ForeignKey(ScaplRole, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Sequence/role association")
        verbose_name_plural = _("Sequence/role associations")

    def __str__(self):
        return self.sequence.description
