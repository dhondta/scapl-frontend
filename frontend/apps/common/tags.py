from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def classname(obj):
    return obj.__class__.__name__


@register.filter
def getattribute(obj, attr):
    if hasattr(obj, str(attr)):
        return getattr(obj, attr)
    elif hasattr(obj, 'has_key') and obj.has_key(attr):
        return obj[attr]


# inspired from: https://github.com/Arpaso/toastmessage/blob/master/toastmessage/templatetags/toastmessage.py
toast_str = "$().toastmessage('%(type)s', '%(message)s');"

js_onload = """<script type="text/javascript">
  $(window).load(function(){
    %s
  });
</script>"""


@register.simple_tag
def toast(message, script_wrap=True):
    res = toast_str % {'message': message, 'type': 'show%sToast' % settings.MESSAGES_TOAST_MAPPING[message.level]}
    if script_wrap:
        res = js_onload % res
    return mark_safe(res)


@register.simple_tag
def toast_all(messages):
    return mark_safe(js_onload % '\n'.join([toast(message, False) for message in messages]))
