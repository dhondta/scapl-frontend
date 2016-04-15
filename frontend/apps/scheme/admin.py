# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from adminsortable2.admin import SortableInlineAdminMixin
from .models import Administrator, Entity, ManualDataItem, ASDataItem, SEDataItem, DataList, DataSequence, \
    ItemListAssociations, ListSequenceAssociations, SequenceRoleAssociations

cadmin = import_module("apps.common.admin")


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

    class Meta:
        model = Administrator

    def email_emphasize_su(self, administrator):
        return format_html((u'<span style="color:red">{}</span>' if administrator.is_superuser else u'{}') \
                           .format(str(administrator)))


class ItemListAssociationsInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ItemListAssociations
    extra = 0


class ListSequenceAssociationsInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ListSequenceAssociations
    extra = 0


class SequenceRoleAssociationsInline(admin.StackedInline):
    model = SequenceRoleAssociations
    extra = 0


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

    def id_code(self, entity):
        return repr(entity)

    def description_overview(self, entity):
        return shorten(entity)

    def save_model(self, request, obj, form, change):
        if getattr(form.instance, 'author', None) is None:
            form.instance.author = request.user
        form.instance.save()


@admin.register(ManualDataItem)
class ManualDataItemAdmin(EntityAdmin):
    actions = (make_item_orphan, )


@admin.register(ASDataItem)
class ASDataItemAdmin(EntityAdmin):
    actions = (make_item_orphan, )
    fieldsets = EntityAdmin.fieldsets + (
        (_('Action'), {
            'fields': ('call', )
        }),
    )
    # TODO: add 'call' validation


@admin.register(SEDataItem)
class SEDataItemAdmin(EntityAdmin):
    actions = (make_item_orphan, )
    fieldsets = EntityAdmin.fieldsets + (
        (_('Action'), {
            'fields': ('api', 'keywords', 'max_suggestions', )
        }),
    )
    # TODO: add 'api' and 'keywords' validation


@admin.register(DataList)
class DataListAdmin(EntityAdmin):
    inlines = (ItemListAssociationsInline, )
    # FIXME: List save returns error "save() prohibited to prevent data loss due to unsaved related object 'list'." if items are provided with the stackedinlines.
    #  see save_model() and save_formset() for a fix


@admin.register(DataSequence)
class DataSequenceAdmin(EntityAdmin):
    fieldsets = EntityAdmin.fieldsets + ((None, {'fields': ('main', )}), )
    inlines = (ListSequenceAssociationsInline, SequenceRoleAssociationsInline, )
    # FIXME: List save returns error "save() prohibited to prevent data loss due to unsaved related object 'sequence'." if items are provided with the stackedinlines.
    #  see save_model() and save_formset() for a fix
