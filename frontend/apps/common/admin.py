# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from .models import GenericUser, Title, Rank, Country, Locality, Address, OrganizationalUnit, Department, Service
from .forms import GenericUserAdminForm, GenericUserCreationForm


class GenericUserAdmin(admin.ModelAdmin):
    form = GenericUserAdminForm
    add_form = GenericUserCreationForm
    change_user_password_template = None
    list_display = ('email_extended', 'service', 'is_active', 'is_staff', )
    list_filter = ('is_active', )
    readonly_fields = ('last_login', 'date_joined', )
    search_fields = ('first_name', 'last_name', 'email', )
    ordering = ('email', )
    fieldsets = (
        (None, {'fields': ('email', ('password1', 'password2', ), )}),
        (_('Personal info'), {'fields': (('first_name', 'last_name', ), ('title', 'rank', ),
                                         'service', ('phone1', 'phone2', ), )}),
        (_('Status'), {'fields': (('last_login', 'date_joined', ), )}),
    )
    add_fieldsets = fieldsets

    class Meta:
        model = GenericUser

    def email_extended(self, admin):
        return str(admin)

    def get_form(self, request, obj=None, **kwargs):
        """ Use special form during user creation """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': admin.utils.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(GenericUserAdmin, self).get_form(request, obj, **defaults)

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
