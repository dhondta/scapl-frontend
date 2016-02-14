# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from adminsortable2.admin import SortableInlineAdminMixin
from .models import Administrator, Entity, ManualDataItem, ASDataItem, SEDataItem, DataList, DataSequence, ItemListAssociations, ListSequenceAssociations

cadmin = import_module("apps.{}.admin".format(settings.COMMON_APP))
forms = import_module("apps.{}.forms".format(settings.COMMON_APP))


def shorten(text):
    try:
        return u'{}...'.format(text.description[0:27]) if len(text.description) > 30 else text.description
    except AttributeError:
        return u'{}...'.format(text.content[0:27]) if len(text.content) > 30 else text.content


def make_item_orphan(modeladmin, request, queryset):
    for obj in queryset:
        ItemListAssociations.objects.filter(item_id=obj.id).delete()
make_item_orphan.short_description = _("Unlink selected Data Items")


def make_list_orphan(modeladmin, request, queryset):
    for obj in queryset:
        ListSequenceAssociations.objects.filter(list_id=obj.id).delete()
make_list_orphan.short_description = _("Unlink selected Data Lists")


class AdministratorAdmin(cadmin.GenericUserAdmin):
    list_display = ('email_emphasize_su', 'service', 'is_active', )
    filter_horizontal = ('user_permissions', )
    fieldsets = (
        (None, {'fields': ('email', ('password1', 'password2', ), )}),
        (_('Personal info'), {'fields': (('first_name', 'last_name', ), ('title', 'rank', ), 'service', ('phone1', 'phone2', ), )}),
        (_('Permissions'), {'fields': (('is_active', 'is_staff', ), 'user_permissions', )}),
        (_('Status'), {'fields': (('last_login', 'date_joined', ), )}),
    )

    class Meta:
        model = Administrator

    def email_emphasize_su(self, administrator):
        return format_html((u'<span style="color:red">{}</span>' if administrator.is_superuser else u'{}') \
                           .format(str(administrator)))


class ItemListAssociationsInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ItemListAssociations
    extra = 1


class ListSequenceAssociationsInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ListSequenceAssociations
    extra = 1


class EntityAdmin(admin.ModelAdmin):
    list_display = ('id_code', 'name', 'description_overview', 'author', 'date_modified', )
    list_filter = ('name', )
    search_fields = ('id', 'name', 'description', )

    class Meta:
        model = Entity

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'author', None) is None:
            obj.author = request.user
        obj.save()

    def id_code(self, entity):
        return str(entity)

    def description_overview(self, entity):
        return shorten(entity)


class DataItemAdmin(EntityAdmin):
    actions = (make_item_orphan, )
    fieldsets = (
        ('Identification', {
            'classes': ['wide', ],
            'fields': ('name', 'description', )
        }),
    )


class ASDataItemAdmin(DataItemAdmin):
    fieldsets = (
        ('Identification', {
            'classes': ['wide', ],
            'fields': ('name', 'description', )
        }),
        ('Action', {
            'fields': ('call', )
        }),
    )
    # TODO: add 'call' validation


class SEDataItemAdmin(DataItemAdmin):
    fieldsets = (
        ('Identification', {
            'classes': ['wide', ],
            'fields': ('name', 'description', )
        }),
        ('Action', {
            'fields': ('api', 'keywords', 'max_suggestions', )
        }),
    )
    # TODO: add 'api' and 'keywords' validation


class DataListAdmin(EntityAdmin):
    inlines = (ItemListAssociationsInline, )
    fieldsets = (
        ('Identification', {
            'classes': ['wide', ],
            'fields': ('name', 'description', )
        }),
    )


class DataSequenceAdmin(EntityAdmin):
    inlines = (ListSequenceAssociationsInline, )
    fieldsets = (
        ('Identification', {
            'classes': ['wide', ],
            'fields': ('name', 'description', )
        }),
        ('Metadata', {
            'fields': ('max_users', )
        })
    )


admin.site.register(Administrator, AdministratorAdmin)
admin.site.register(ManualDataItem, DataItemAdmin)
admin.site.register(ASDataItem, ASDataItemAdmin)
admin.site.register(SEDataItem, SEDataItemAdmin)
admin.site.register(DataList, DataListAdmin)
admin.site.register(DataSequence, DataSequenceAdmin)
