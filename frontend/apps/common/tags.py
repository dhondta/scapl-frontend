from django import template

register = template.Library()


@register.filter
def getattr(obj, val):
    return getattr(obj, val)
