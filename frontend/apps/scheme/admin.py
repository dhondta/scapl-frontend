# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from adminsortable2.admin import SortableInlineAdminMixin
from .models import Administrator, Entity, ManualDataItem, ASDataItem, SEDataItem, DataList, DataSequence, \
    ItemListAssociations, ListSequenceAssociations, SequenceRoleAssociations

cadmin = import_module("apps.{}.admin".format(settings.COMMON_APP))
forms = import_module("apps.{}.forms".format(settings.COMMON_APP))


def shorten(text, length=50):
    try:
        return u'{}...'.format(text.description[0:27]) if len(text.description) > length else text.description
    except AttributeError:
        return u'{}...'.format(text.content[0:27]) if len(text.content) > length else text.content


def make_item_orphan(modeladmin, request, queryset):
    for obj in queryset:
        ItemListAssociations.objects.filter(item_id=obj.id).delete()
make_item_orphan.short_description = _("Unlink selected Data Items")


def make_list_orphan(modeladmin, request, queryset):
    for obj in queryset:
        ListSequenceAssociations.objects.filter(list_id=obj.id).delete()
make_list_orphan.short_description = _("Unlink selected Data Lists")


@admin.register(Administrator)
class AdministratorAdmin(cadmin.GenericUserAdmin):
    list_display = ('email_emphasize_su', 'service', 'is_active', )
    filter_horizontal = ('user_permissions', )
    fieldsets = (
        (None, {'fields': ('email', ('password1', 'password2', ), )}),
        (_('Personal info'), {'fields': (('first_name', 'last_name', ), ('title', 'rank', ), 'service', ('phone1', 'phone2', ), )}),
        (_('Permissions'), {'fields': (('is_active', 'is_staff', ), 'user_permissions', )}),
        (_('Status'), {'fields': (('last_login', 'date_joined', ), )}),
    )
    add_fieldsets = fieldsets

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


class SequenceRoleAssociationsInline(admin.StackedInline):
    model = SequenceRoleAssociations
    extra = 1


class EntityAdmin(admin.ModelAdmin):
    list_display = ('id_code', 'name', 'description_overview', 'author', 'date_modified', )
    list_filter = ('name', )
    search_fields = ('id', 'name', 'description', )
    fieldsets = (
        (_('Identification'), {
            'classes': ['wide', ],
            'fields': ('name', 'description', )
        }),
    )

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


@admin.register(ManualDataItem)
class DataItemAdmin(EntityAdmin):
    actions = (make_item_orphan, )


@admin.register(ASDataItem)
class ASDataItemAdmin(DataItemAdmin):
    fieldsets = EntityAdmin.fieldsets + (
        (_('Action'), {
            'fields': ('call', )
        }),
    )
    # fieldsets = (
    #     EntityAdmin.fieldsets[0],
    #     (_('Action'), {
    #         'fields': ('call', )
    #     }),
    # )
    # TODO: add 'call' validation


@admin.register(SEDataItem)
class SEDataItemAdmin(DataItemAdmin):
    fieldsets = EntityAdmin.fieldsets + (
        (_('Action'), {
            'fields': ('api', 'keywords', 'max_suggestions', )
        }),
    )
    # TODO: add 'api' and 'keywords' validation


@admin.register(DataList)
class DataListAdmin(EntityAdmin):
    inlines = (ItemListAssociationsInline, )


@admin.register(DataSequence)
class DataSequenceAdmin(EntityAdmin):
    inlines = (ListSequenceAssociationsInline, SequenceRoleAssociationsInline, )
