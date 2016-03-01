# -*- coding: UTF-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import APLTask, APLTaskItem, APLTaskContributors
from .msform import FormWizard


class DataItemForm(forms.Form):
    """ A form handling a data item (DI) """



class DataListForm(forms.Form):
    """ A form handling a data list (DL) """
    def save(self, commit=True):
        dl = super(StepForm, self).save(commit=False)
        if commit:
            user.save()
        return dl


class DataSequenceForm(FormWizard):
    """ A multi-step form handling a data sequence (DS) """
    def done(self, request, form_list):
        return request, form_list
