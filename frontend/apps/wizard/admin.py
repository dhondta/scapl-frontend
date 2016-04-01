# -*- coding: UTF-8 -*-
from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import APLTask, APLStatus, APLTaskContributors, APLTaskItem


@admin.register(APLStatus)
class MyModelAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


admin.site.register(APLTask)
admin.site.register(APLTaskItem)
admin.site.register(APLTaskContributors)
