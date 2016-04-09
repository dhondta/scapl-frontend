# -*- coding: UTF-8 -*-
from django.template.defaultfilters import timesince
from django.utils.translation import ugettext_lazy as _


class ProgressString(str):
    html_progress_bar = """<div class="progress">
          <div class="progress-bar progress-bar-{1}  progress-bar-striped active" role="progressbar" aria-valuenow="{0}"
              aria-valuemin="0" aria-valuemax="100" style="width:{0}%">{0}%</div>
        </div>"""

    def __new__(cls, nbr):
        lvl = 'danger' if nbr < 30 else 'warning' if nbr < 70 else 'info' if nbr < 100 else 'success'
        return super(ProgressString, cls).__new__(cls, ProgressString.html_progress_bar.format(nbr, lvl))


class TaskOptions(object):
    html_option = """
        """

    def __new__(self):
        pass


reports_template = {
    'title': _('List of generated reports'),
    'order': ['reference', 'author'],
    'fields': {
        'reference': {
            'header': _('APL Reference'),
            'value': lambda obj: obj.reference,
        },
        'author': {
            'header': _('Author'),
            'value': lambda obj: obj.author.get_short_name(),
        },
    }
}


tasks_template = {
    'title': _('List of pending APL tasks'),
    'order': ['reference', 'author', 'contributors', 'timesincec', 'timesincem', 'progress', 'options'],
    'fields': {
        'reference': {
            'header': _('APL Reference'),
            'value': lambda obj: obj.reference,
        },
        'author': {
            'header': _('Author'),
            'value': lambda obj: obj.author.get_short_name(),
        },
        'contributors': {
            'header': _('Contributors'),
            'value': lambda obj: '<br>'.join([x.get_short_name() for x in obj.contributors.all()]),
        },
        'timesincec': {
            'header': _('Time since creation'),
            'value': lambda obj: timesince(obj.date_created)
        },
        'timesincem': {
            'header': _('Time since last modification'),
            'value': lambda obj: timesince(obj.date_modified)
        },
        'progress': {
            'header': _('Progress'),
            'value': lambda obj: ProgressString(obj.progress),
        },
        'options': {
            'header': _('Options'),
            'value': '',
        },
    }
}
