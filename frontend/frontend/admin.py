# -*- coding: UTF-8 -*-
from django.utils.translation import ugettext_lazy as _

# admin_reorder settings
ADMIN_REORDER = (
    # Keep original label and models
    'sites',
    # Reorder Wizard Scheme
    {
        'app': 'scheme',
        'label': _("1- Wizard Scheme Design"),
        'models': (
            'scheme.Administrator',
            'scheme.DataSequence',
            'scheme.DataList',
            'scheme.ManualDataItem',
            'scheme.SEDataItem',
            'scheme.ASDataItem',
        )
    },
    {
        'app': 'common',
        'label': _("2- General Information"),
    },
    {
        'app': 'profiles',
        'label': _("3- User Profile Information"),
    },
    {
        'app': 'wizard',
        'label': _("4- Wizard Elements"),
        'models': (
            {'model': 'wizard.Task', 'label': 'APL'},
            {'model': 'wizard.Status', 'label': 'Status hierarchy'},
        )
    },
    {
        'app': 'djcelery',
        'label': _("5- Celery Components"),
    },
    {
        'app': 'tooltips',
        'label': _('6- Add-ons'),
        'models': (
            {'model': 'tooltips.Tooltip', 'label': 'Tooltips'},
            {'model': 'admin_honeypot.LoginAttempt', 'label': 'Login attempts (Admin Honeypot)'},
        )
    },
)
