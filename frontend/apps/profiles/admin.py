# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from .models import NormalUser, SecurityUser, ScaplRole

cadmin = import_module("apps.{}.admin".format(settings.COMMON_APP))
sadmin = import_module("apps.{}.admin".format(settings.SCHEME_APP))


def scapl_user_admin(model=None):
    class ScaplUserAdmin(cadmin.GenericUserAdmin):
        list_display = cadmin.GenericUserAdmin.list_display + ('role',)
        list_filter = cadmin.GenericUserAdmin.list_filter + ('role',)
        fieldsets = (
            (None, {'fields': ('email', ('password1', 'password2', ), )}),
            (_('Personal info'), {'fields': (('first_name', 'last_name', ), ('title', 'rank', ),
                                             ('service', 'role', ), ('phone1', 'phone2', ), )}),
            (_('Status'), {'fields': (('last_login', 'date_joined', ), )}),
        )
        add_fieldsets = fieldsets

        def get_form(self, request, obj=None, **kwargs):
            form = super(ScaplUserAdmin, self).get_form(request, obj, **kwargs)
            form.base_fields['role'].queryset = ScaplRole.objects \
                .filter(scope__in=[0, [NormalUser, SecurityUser].index(self.model) + 1])
            return form

        def queryset(self, request):
            qs = super(ScaplUserAdmin, self).queryset(request)
            if model:
                qs = qs.filter(type=[NormalUser, SecurityUser].index(model))
            return qs

    return ScaplUserAdmin


@admin.register(ScaplRole)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'scope', 'author', 'date_modified', )
    list_filter = ('name', )
    readonly_fields = ('id', 'author', )
    search_fields = ('id', 'name', 'description', )
    ordering = ('name', 'scope', )
    fieldsets = (
        (_('Identification'), {
            'classes': ['wide', ],
            'fields': ('name', 'description', 'scope', )
        }),
    )


admin.site.register(NormalUser, scapl_user_admin(NormalUser))
admin.site.register(SecurityUser, scapl_user_admin(SecurityUser))
