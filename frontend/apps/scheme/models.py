# -*- coding: UTF-8 -*-
import json
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from model_utils.managers import InheritanceManager


cmodels = import_module("apps.common.models")
pmodels = import_module("apps.profiles.models")

""" (see SCAPL's SDD section 4.2 Data Dictionary for more details about the data scheme and models' meaning) """


class AdministratorManager(cmodels.GenericUserManager):
    def get_queryset(self):
        return super(AdministratorManager, self).get_queryset().filter(type=2)


class Administrator(pmodels.ScaplUser):
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
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(null=True)
    date_created = models.DateTimeField(verbose_name=_(u'Creation date'), auto_now_add=True, auto_now=False, editable=False)
    date_modified = models.DateTimeField(verbose_name=_(u'Last modification date'), auto_now_add=False, auto_now=True, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class DataSequence(Entity):
    """ This model defines the structure of a data sequence """
    author = models.ForeignKey(pmodels.ScaplUser, null=True, blank=True, related_name="created_sequences")
    roles = models.ManyToManyField(pmodels.ScaplRole, through='SequenceRoleAssociations', related_name="related_sequences")
    max_users = models.IntegerField(default=5)
    main = models.BooleanField(default=False)

    class Meta:
        ordering = ('id', )
        verbose_name = _("Data sequence")
        verbose_name_plural = _("Data sequences")

    def __repr__(self):
        return u'DS{}'.format(str(self.id).zfill(settings.DS_ID_DIGITS))

    def save(self, *args, **kwargs):
        if self.main:
            for ds in DataSequence.objects.all():
                if ds.main:
                    ds.main = False
                    ds.save()
        return super(DataSequence, self).save(*args, **kwargs)


class DataList(Entity):
    """ This model defines the structure of a data list """
    author = models.ForeignKey(pmodels.ScaplUser, null=True, blank=True, related_name="created_lists")
    sequences = models.ManyToManyField(DataSequence, through='ListSequenceAssociations', related_name="lists")

    class Meta:
        ordering = ('id', )
        verbose_name = _("Data list")
        verbose_name_plural = _("Data lists")

    def __repr__(self):
        return u'DL{}'.format(str(self.id).zfill(settings.DL_ID_DIGITS))


class DataItem(Entity):
    """ This model defines the generic structure of a data item """
    author = models.ForeignKey(pmodels.ScaplUser, null=True, blank=True, related_name="created_items")
    lists = models.ManyToManyField(DataList, through='ItemListAssociations', related_name="items")
    objects = InheritanceManager()

    class Meta:
        ordering = ('id', )

    def __repr__(self):
        return u'DI{}'.format(str(self.id).zfill(settings.DI_ID_DIGITS))


class ManualDataItem(DataItem):
    """ This model defines a manual data item (not triggering any task) """

    class Meta:
        verbose_name = _("Data item (Manual)")
        verbose_name_plural = _("Data items (Manual)")


class ASDataItem(DataItem):
    """ This model defines the structure of a data item particularized to the Automation System """
    call = models.TextField()

    class Meta:
        verbose_name = _("Data item (Automation System)")
        verbose_name_plural = _("Data items (Automation System)")


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
    role = models.ForeignKey(pmodels.ScaplRole, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Sequence/role association")
        verbose_name_plural = _("Sequence/role associations")

    def __str__(self):
        return self.sequence.description


class PluginParameter(models.Model):
    name = models.CharField(max_length=120)
    label = models.TextField(blank=True, null=True, default=None)
    type = models.IntegerField(choices=((0, 'string', ), (1, 'integer', ), (2, 'list', ), ), default=0)

    def __repr__(self):
        return '{}:{}'.format(self.type, self.name)

    def __str__(self):
        return self.name


class Plugin(Entity):
    slug = models.SlugField(max_length=30)
    parameters = models.ForeignKey(PluginParameter)

    def __repr__(self):
        return self.slug
