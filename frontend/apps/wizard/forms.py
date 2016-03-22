# -*- coding: UTF-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from .models import APLTaskItem
from .msform import MultiFormWizard


class APLTaskItemForm(forms.Form):
    """ A form handling an APL task item """

    class Meta:
        model = APLTaskItem
        fields = ('apl', 'item', 'value', )


class DataSequenceForm(MultiFormWizard):
    """ A multi-step form handling a data sequence (DS) """
    def done(self, request, form_list):
        return request, form_list
