# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from .models import GenericUser, Title, Rank, Country, Locality, Address, OrganizationalUnit, Department, Service
from .forms import GenericUserAdminForm, GenericUserCreationForm


class GenericUserAdmin(UserAdmin):
    change_user_password_template = None
    list_display = ('email_extended', 'service', 'is_active', 'is_staff', )
    list_filter = ('is_active', )
    search_fields = ('first_name', 'last_name', 'email', )
    ordering = ('email', )
    update_form = GenericUserAdminForm
    update_readonly_fields = ('last_login', 'date_joined', )
    update_fieldsets = (
        (_('Personal info'), {'fields': (('first_name', 'last_name', ), ('title', 'rank', ),
                                         'service', ('phone1', 'phone2', ), )}),
        (_('Permissions'), {'fields': ('user_permissions', )}),
        (_('Status'), {'fields': ('is_active', ('date_joined', 'last_login', ), )}),
    )
    add_form = GenericUserCreationForm
    add_fieldsets = (
        (_('Credentials'), {'fields': ('email', ('new_password1', 'new_password2', ), )}),
    )
    superuser_fieldsets = (
        (_('Personal info'), {'fields': (('first_name', 'last_name', ), ('title', 'rank', ),
                                         'service', ('phone1', 'phone2', ), )}),
    )

    class Meta:
        model = GenericUser

    def __init__(self, *args, **kwargs):
        super(GenericUserAdmin, self).__init__(*args, **kwargs)
        for attr in ['update_exclude', 'add_exclude']:
            if not hasattr(self, attr):
                setattr(self, attr, ())

    def email_extended(self, user):
        return str(user)

    def get_actions(self, request, obj=None):
        actions = super(GenericUserAdmin, self).get_actions(request)
        if obj and obj.is_superuser:
            del actions['delete_selected']
        return actions

    def get_form(self, request, obj=None, **kwargs):
        """ Use special form during user creation and prevent from modifying is_active and is_staff for superuser """
        if obj is None:
            kwargs['form'] = self.add_form
            kwargs['fields'] = flatten_fieldsets(self.add_fieldsets)
            kwargs['exclude'] = self.add_exclude
            self.fieldsets = self.add_fieldsets
            self.readonly_fields = ()
        else:
            kwargs['form'] = self.update_form
            kwargs['fields'] = flatten_fieldsets(self.update_fieldsets)
            if not obj.is_superuser:
                kwargs['exclude'] = self.update_exclude + self.update_readonly_fields
                self.readonly_fields = self.update_readonly_fields
            else:
                self.readonly_fields = kwargs['exclude'] = flatten_fieldsets(self.update_fieldsets)
            self.fieldsets = self.update_fieldsets
        return super(GenericUserAdmin, self).get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return super(GenericUserAdmin, self).get_readonly_fields(request, obj)
        else:
            return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return obj and not obj.is_superuser

    def lookup_allowed(self, lookup, value):
        # See #20078: we don't want to allow any lookups involving passwords.
        if lookup.startswith('password'):
            return False
        return super(GenericUserAdmin, self).lookup_allowed(lookup, value)


admin.site.unregister(Group)
admin.site.register(Title)
admin.site.register(Rank)
admin.site.register(Country)
admin.site.register(Locality)
admin.site.register(Address)
admin.site.register(OrganizationalUnit)
admin.site.register(Department)
admin.site.register(Service)
