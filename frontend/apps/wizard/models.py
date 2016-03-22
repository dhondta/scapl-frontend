# -*- coding: UTF-8 -*-
import json
from django.apps import apps
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

user_app, user_model = settings.AUTH_USER_MODEL.split('.')
GenericUser = apps.get_app_config(user_app).get_model(user_model)

""" (see SCAPL's SDD section 4.2 Data Dictionary for more details about the data scheme and models' meaning) """


#def apl_packages_path(instance, filename):
#    return 'packages/apl_{}/{}'.format(instance.apl.id, filename)


class Package(models.Model):
    id = models.IntegerField(primary_key=True)
    file = models.FileField(upload_to=lambda i, f: 'packages/apl_{}/{}'.format(i.apl.id, f))


class APLTask(models.Model):
    id = models.IntegerField(primary_key=True)
    reference = models.CharField(max_length=64)
    author = models.ForeignKey(GenericUser, null=True, blank=True, related_name="created_tasks")
    contributors = models.ManyToManyField(GenericUser, through='APLTaskContributors', related_name="contributors")
    keywords = models.CharField(max_length=1024)  # TODO: change it to JSONField (Django 1.9+ if used with PostgreSQL)
    packages = models.ForeignKey(Package)

    class Meta:
        verbose_name = _("APL file creation task")
        verbose_name_plural = _("APL file creation tasks")

    def setkeywords(self, keywords):  # TODO: this is error-prone due to the field's length ; add a validation
        self.keywords = json.dumps(keywords)

    def getkeywords(self):
        return json.loads(self.keywords)

    def __str__(self):
        return self.reference


class APLTaskContributors(models.Model):
    apl = models.ForeignKey(APLTask, on_delete=models.CASCADE)
    contributor = models.ForeignKey(GenericUser, on_delete=models.CASCADE)

    class Meta:
        ordering = ('apl', 'contributor', )
        verbose_name = _("APL task contributor")
        verbose_name_plural = _("APL task contributors")

    def __str__(self):
        return str(self.contributor)


class APLTaskItem(models.Model):
    apl = models.ForeignKey(APLTask, on_delete=models.CASCADE)
    item = models.IntegerField(blank=False, null=False, editable=False)
    value = models.TextField()
    date_filled = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('apl', 'item', )
