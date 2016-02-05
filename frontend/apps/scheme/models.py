# -*- coding: UTF-8 -*-
import json
from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

user_app, user_model = settings.AUTH_USER_MODEL.split('.')
DI_ID_DIGITS = 5
DL_ID_DIGITS = 3
DS_ID_DIGITS = 2

""" (see SDD section 4.2 Data Dictionary for more details about the data scheme and models' meaning) """


class Administrator(apps.get_app_config(user_app).get_model(user_model)):
    """ This model defines an administrator for the wizard application """
    def create_superuser(self, email, date_of_birth, password):
        user = self.create_user(email=email, date_of_birth=date_of_birth, password=password, is_staff=True)
        user.save(using=self._db)
        return user


class Entity(models.Model):
    """ This model defines the generic structure of a data entity """
    name = models.CharField(max_length=120)
    description = models.TextField(null=True)
    date_created = models.DateTimeField(verbose_name=_(u'Creation date'), auto_now_add=True, auto_now=False, editable=False)
    date_modified = models.DateTimeField(verbose_name=_(u'Last modification date'), auto_now_add=True, auto_now=True, editable=False)

    class Meta:
        unique_together = ('name', 'description', )
        abstract = True


class DataSequence(Entity):
    """ This model defines the structure of a data sequence """
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(Administrator, null=True, blank=True, related_name="created_sequences")
    max_users = models.IntegerField()
    user = models.ManyToManyField(apps.get_app_config(user_app).get_model(user_model), related_name="sequences")

    def __str__(self):
        return u'DS{}'.format(str(self.id).zfill(DS_ID_DIGITS))


class DataList(Entity):
    """ This model defines the structure of a data list """
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(Administrator, null=True, blank=True, related_name="created_lists")
    sequence = models.ManyToManyField(DataSequence, related_name="lists")

    def __str__(self):
        return u'DL{}'.format(str(self.id).zfill(DL_ID_DIGITS))


class DataItem(Entity):
    """ This model defines the generic structure of a data item """
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(Administrator, null=True, blank=True, related_name="created_items")
    list = models.ManyToManyField(DataList, related_name="items")

    class Meta:
        verbose_name_plural = "Data items (Manual)"

    def __str__(self):
        return u'DI{}'.format(str(self.id).zfill(DI_ID_DIGITS))


class ASDataItem(DataItem):
    """ This model defines the structure of a data item particularized to the Automation System """
    call = models.TextField()

    class Meta:
        verbose_name_plural = "Data items (Automation System)"

    def __repr__(self):
        return u'{}'.format(self.call)


class SEDataItem(DataItem):
    """ This model defines the structure of a data item particularized to the Search Engine """
    max_suggestions = models.IntegerField(default=0)
    keywords = models.CharField(max_length=256)  # TODO: change it to JSONField (Django 1.9+ if used with PostgreSQL)
    api = models.TextField()

    class Meta:
        verbose_name_plural = "Data items (Search Engine)"

    def setkeywords(self, keywords):  # TODO: this is error-prone due to the field's length ; add a validation
        self.keywords = json.dumps(keywords)

    def getkeywords(self):
        return json.loads(self.keywords)

    def __repr__(self):
        return u'{} {} {}'.format(self.api, self.keywords, self.max_suggestions)
