# -*- coding: UTF-8 -*-
from datetime import timedelta
from django.conf import settings
from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Status, Task, TaskContributors, TaskItem, TaskItemResult


@admin.register(Status)
class StatusAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


@admin.register(TaskItemResult)
class TaskItemResultAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('task_repr', 'date_created', 'expires_on', )
    list_display_links = None
    search_fields = ('task', )
    fieldsets = ((None, {'fields': ()}), )

    def expires_on(self, obj):
        return obj.date_triggered + timedelta(seconds=self.expires_after)

    def has_add_permission(self, request):
        return False

    def task_repr(self, obj):
        return repr(obj.task)


admin.site.register(Task)
admin.site.register(TaskItem)
admin.site.register(TaskContributors)
