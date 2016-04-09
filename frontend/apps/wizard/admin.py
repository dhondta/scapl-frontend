# -*- coding: UTF-8 -*-
from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Task, Status, TaskContributors, TaskItem


@admin.register(Status)
class StatusAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


admin.site.register(Task)
admin.site.register(TaskItem)
admin.site.register(TaskContributors)
