import json
from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django_summernote.widgets import SummernoteInplaceWidget, _get_proper_language, __summernote_options__


class AdminSummernoteInplaceWidget(SummernoteInplaceWidget):
    config = {
        'iframe': False,
        'airMode': False,
        'styleWithTags': True,
        'disableDragAndDrop': True,
        'direction': 'ltr',
        'width': '100%',
        'height': '200',
        'lang': 'en-US',
        'lang_matches': {
            'en': 'en-US',
            'fr': 'fr-FR',
            'nl': 'nl-NL',
        },
        'toolbar': [
            ['action', ['undo', 'redo']],
            ['font', ['bold', 'italic', 'underline']],
            ['font', ['fontname', 'fontsize', 'color']],
            ['insert', ['link']],
        ],
        'disable_upload': True,
        'prettifyHtml': False,
    }

    def render(self, name, value, attrs=None):
        attrs_for_textarea = attrs.copy()
        attrs_for_textarea['hidden'] = 'true'
        attrs_for_textarea['id'] += '-textarea'
        html = super(AdminSummernoteInplaceWidget, self).render(name, value, attrs_for_textarea)
        html += render_to_string(
            'django_summernote/widget_iframe.html',
            Context(dict({
                'id': attrs['id'].replace('-', '_'),
                'id_src': attrs['id'],
                'value': value if value else '',
                'settings': json.dumps(self.template_contexts()),
                'STATIC_URL': settings.STATIC_URL,
            }))
        )
        return mark_safe(html)

    def template_contexts(self):
        contexts = {'lang': _get_proper_language()}
        for option in __summernote_options__:
            v = self.attrs.get(option, self.config.get(option))
            if v:
                contexts[option] = v
        return contexts
