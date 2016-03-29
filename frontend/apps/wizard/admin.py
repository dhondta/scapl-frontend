# -*- coding: UTF-8 -*-
from django.contrib import admin
from .models import APLTask, APLTaskContributors, APLTaskItem


admin.site.register(APLTask)
admin.site.register(APLTaskItem)
admin.site.register(APLTaskContributors)
