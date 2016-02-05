# -*- coding: UTF-8 -*-
from django.contrib import admin
from .models import Administrator, Entity, DataItem, ASDataItem, SEDataItem, DataList, DataSequence
from .forms import AdminsitratorAddForm, AdminsitratorUpdateForm
from django.utils.translation import ugettext_lazy as _


def shorten(text):
    try:
        return u'{}...'.format(text.description[0:27]) if len(text.description) > 30 else text.description
    except AttributeError:
        return u'{}...'.format(text.content[0:27]) if len(text.content) > 30 else text.content

"""
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    groups = models.ForeignKey(Group, default=None)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    title = models.ForeignKey(Title, default=None, blank=True, null=True, related_name="users")
    rank = models.ForeignKey(Rank, default=None, blank=True, null=True, related_name="users")
    service = models.ForeignKey(Service, default=None, blank=True, null=True, related_name="users")
    phone1 = models.CharField(max_length=30, default=None, blank=True, null=True)
    phone2 = models.CharField(max_length=30, default=None, blank=True, null=True)
    comments = models.TextField(max_length=1000, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
"""


class AdministratorAdmin(admin.ModelAdmin):
    form = AdminsitratorUpdateForm
    add_form = AdminsitratorAddForm
    list_display = ('email', 'is_email_verified', 'service', 'is_staff', )
    list_filter = ('is_active', 'is_email_verified', )
    search_fields = ('first_name', 'last_name', 'email', )
    ordering = ('email', )
    fieldsets = (
        (None, {'fields': ('email', 'password', )}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'title', 'rank', 'service', 'phone1', 'phone2', )}),
        (_('Permissions'), {'fields': ('is_active', 'is_email_verified', 'is_staff', 'groups', 'user_permissions', )}),
        (_('Status'), {'fields': ('last_login', 'date_joined', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    class Meta:
        model = Administrator


class EntityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description_overview', 'author', 'date_modified', )
    list_filter = ('name', )
    search_fields = ('id', 'name', 'description', )

    class Meta:
        model = Entity

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()

    def description_overview(self, description):
        return shorten(description)


class DataItemAdmin(EntityAdmin):
    fieldsets = (
        ('Identification', {
            'classes': ['collapse', ],
            'fields': ('name', 'list', )
        }),
        ('Metadata', {
            'fields': ('description', )
        })
    )


class ASDataItemAdmin(DataItemAdmin):
    fieldsets = (
        ('Identification', {
            'classes': ['collapse', ],
            'fields': ('name', 'list', )
        }),
        ('Metadata', {
            'fields': ('description', )
        }),
        ('Action', {
            'fields': ('call', )
        })
    )
    # TODO: add 'call' validation


class SEDataItemAdmin(DataItemAdmin):
    fieldsets = (
        ('Identification', {
            'classes': ['collapse', ],
            'fields': ('name', 'list', )
        }),
        ('Metadata', {
            'fields': ('description', )
        }),
        ('Action', {
            'fields': ('api', 'keywords', 'max_suggestions', )
        })
    )
    # TODO: add 'api' and 'keywords' validation


class DataListAdmin(EntityAdmin):
    fieldsets = (
        ('Identification', {
            'classes': ['collapse', ],
            'fields': ('name', 'sequence', )
        }),
        ('Metadata', {
            'fields': ('description', )
        })
    )


class DataSequenceAdmin(EntityAdmin):
    fieldsets = (
        ('Identification', {
            'classes': ['collapse', ],
            'fields': ('name', )
        }),
        ('Metadata', {
            'fields': ('description', )
        })
    )


admin.site.register(Administrator, AdministratorAdmin)
admin.site.register(DataItem, DataItemAdmin)
admin.site.register(ASDataItem, ASDataItemAdmin)
admin.site.register(SEDataItem, SEDataItemAdmin)
admin.site.register(DataList, DataListAdmin)
admin.site.register(DataSequence, DataSequenceAdmin)