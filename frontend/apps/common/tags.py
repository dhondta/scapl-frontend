from django import template

register = template.Library()


@register.filter
def classname(obj):
    return obj.__class__.__name__


@register.filter
def getattribute(obj, attr):
    print(obj.__dict__)
    if hasattr(obj, str(attr)):
        return getattr(obj, attr)
    elif hasattr(obj, 'has_key') and obj.has_key(attr):
        return obj[attr]
