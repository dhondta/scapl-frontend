# -*- coding: UTF-8 -*-
import re
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords
from importlib import import_module

pmodels = import_module("apps.profiles.models")
smodels = import_module("apps.scheme.models")

""" (see SCAPL's SDD section 4.2 Data Dictionary for more details about the data scheme and models' meaning) """


def upload_packages(instance, filename):
    return 'packages/apl_{}/{}'.format(instance.apl.id, filename)


class Package(models.Model):
    file = models.FileField(upload_to=upload_packages)


class Status(models.Model):
    status = models.CharField(max_length=32, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ('order', )
        verbose_name = verbose_name_plural = _("Status")

    def save(self, *args, **kwargs):
        self.status = self.status.upper()
        super(Status, self).save(*args, **kwargs)

    def __str__(self):
        return self.status


class Report(models.Model):
    document = models.FileField(upload_to=settings.REPORTS_LOCATION)
    date_generated = models.DateTimeField(verbose_name=_(u'Generation date'), auto_now_add=True, auto_now=False, editable=False)

    class Meta:
        verbose_name = _("Report")
        verbose_name_plural = _("Reports")


class Task(models.Model):
    author = models.ForeignKey(pmodels.ScaplUser, related_name="created_tasks")
    contributors = models.ManyToManyField(pmodels.ScaplUser, through='TaskContributors', related_name="apl_tasks")
    keywords = models.CharField(max_length=1024, unique=True)  # TODO: change it to JSONField (Django 1.9+ if used with PostgreSQL)
    packages = models.ForeignKey(Package, blank=True, null=True, default=None)
    code = models.CharField(max_length=8, blank=True, null=True, editable=False)
    status = models.ForeignKey(Status, blank=True, null=True, editable=False, default=None, related_name="related_tasks")
    date_created = models.DateTimeField(verbose_name=_(u'Creation date'), auto_now_add=True, auto_now=False, editable=False)
    date_modified = models.DateTimeField(verbose_name=_(u'Last modification date'), auto_now_add=False, auto_now=True, editable=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")

    def __repr__(self):
        return u'APL{}'.format(str(self.id).zfill(settings.APL_ID_DIGITS))

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.status:
            status = Status.objects.filter(order=1)
            self.status = 'UNDEFINED' if len(status) == 0 else status[0]
        super(Task, self).save(*args, **kwargs)
        if not self.code:
            self.code = "{}_{}".format(now().year, str(self.pk or 'X' * 3).zfill(3))
        kwargs.update({'update_fields': ['code']})
        super(Task, self).save(*args, **kwargs)

    # TODO: this is error-prone due to the field's length ; add a validation
    # def setkeywords(self, keywords):
    #     self.keywords = json.dumps(keywords)
    #
    # def getkeywords(self):
    #     return json.loads(self.keywords)

    @property
    def progress(self):
        m = len([x for x in TaskItem.objects.filter(apl=self) if x.is_valid])
        n = smodels.DataItem.objects.count()
        return int(100 * m / n) if n > 0 else 0

    @property
    def reference(self):
        return "{}_{}".format(self.code, self.status) if self.status else self.code


class TaskContributors(models.Model):
    apl = models.ForeignKey(Task, on_delete=models.CASCADE)
    contributor = models.ForeignKey(pmodels.ScaplUser, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(verbose_name=_(u'Join date'), auto_now_add=True, auto_now=False, editable=False)

    class Meta:
        ordering = ('apl', 'contributor', )
        verbose_name = _("Contributor")
        verbose_name_plural = _("Contributors")

    def __str__(self):
        return str(self.contributor)


class TaskHistory(models.Model):
    apl = models.ForeignKey(Task, on_delete=models.CASCADE)
    reference = models.CharField(max_length=32, editable=False)
    date_created = models.DateTimeField(auto_now_add=True, auto_now=False, editable=False)
    date_last_modified = models.DateTimeField(auto_now_add=True, auto_now=False, editable=False)


class TaskItem(models.Model):
    apl = models.ForeignKey(Task)
    item = models.ForeignKey(smodels.DataItem, related_name="task_items")
    value = models.TextField(default=None, blank=True, null=True)
    date_filled = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = ('apl', 'item', )
        verbose_name = _("Item")
        verbose_name_plural = _("Items")

    def __repr__(self):
        return '{}-{}'.format(repr(self.apl), repr(self.item))

    def __str__(self):
        return '{}/{}'.format(self.apl.reference, repr(self.item))

    @property
    def is_valid(self):
        return self.value is not None and not re.sub(r'^\<p\>', '', re.sub(r'\<\/p\>$', '', str(self.value))) in ['', '<br>']


class TaskItemResult(models.Model):
    task = models.ForeignKey(TaskItem)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    expires_after = models.IntegerField(default=settings.ASYNC_TASK_EXPIRATION, editable=False)

    class Meta:
        verbose_name = _("Asynchronous task")
        verbose_name_plural = _("Asynchronous tasks")

    def __str__(self):
        return repr(self.task)
