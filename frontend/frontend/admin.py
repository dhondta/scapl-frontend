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
        'models': (
            'common.Country',
            'common.Locality',
            'common.Address',
            'common.OrganizationalUnit',
            'common.Department',
            'common.Service',
            'common.Rank',
            'common.Title',
        )
    },
    {
        'app': 'profiles',
        'label': _("3- User Profile Information"),
        'models': (
            'profiles.NormalUser',
            'profiles.SecurityUser',
            'profiles.ScaplRole',
        )
    },
    {
        'app': 'wizard',
        'label': _("4- Wizard Elements"),
        'models': (
            {'model': 'wizard.Task', 'label': 'APL'},
            {'model': 'wizard.Status', 'label': 'Status hierarchy'},
            {'model': 'wizard.TaskItemResult', 'label': 'Triggered asynchronous tasks'},
        )
    },
    {
        'app': 'common',
        'label': _('5- Add-ons'),
        'models': (
            {'model': 'common.Tooltip', 'label': 'Tooltips'},
            {'model': 'admin_honeypot.LoginAttempt', 'label': 'Login attempts (Admin Honeypot)'},
        )
    },
)
