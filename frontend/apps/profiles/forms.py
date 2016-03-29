# -*- coding: UTF-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from importlib import import_module
from .models import ScaplUser

cforms = import_module("apps.{}.forms".format(settings.COMMON_APP))

# TODO: Add avatar management (see https://github.com/bitmazk/django-user-media)

class ThemeSpecificMixin(object):
    """ A mix-in for handling theme-specific HTML attributes """

    def __init__(self, *args, **kwargs):
        super(ThemeSpecificMixin, self).__init__(*args, **kwargs)
        self.form_title = _("Edit your profile")
        self.fields['email'].widget.attrs['disabled'] = ''
        # Neon them-specific attributes settings
        for field in self.fields.keys():
            # ensure 'id' attribute is present for all fields
            self.fields[field].widget.attrs['id'] = field
            # add 'form-control' attribute to all fields
            self.fields[field].widget.attrs['class'] = 'form-control'  # Neon them-specific
            # add 'placeholder' attribute to all fields
            try:
                self.fields[field].widget.attrs['placeholder'] = self.fields[field].label
            except KeyError:
                self.fields[field].widget.attrs['placeholder'] = field.capitalize().replace("_", " ")
            # add 'data-mask' attribute for specific fields
            if field == 'email':
                self.fields[field].widget.attrs['data-mask'] = 'email'
            elif 'date' in field:
                self.fields[field].widget.attrs['data-mask'] = 'date'
            elif 'phone' in field:
                self.fields[field].widget.attrs['data-mask'] = '^(\+\d{1,3}\s|0)?\(?\d{3}\)?\/?([\s.-]?\d{3}[\s.-]?\d{4}|\d{2}\.?\d{2}\.?\d{2})$'
                self.fields[field].widget.attrs['data-is-regex'] = 'true'
            # add 'autocomplete' attribute for all fields
            self.fields[field].widget.attrs['autocomplete'] = 'off'


class ScaplUserUpdateForm(ThemeSpecificMixin, cforms.GenericUserUpdateForm):
    """ An extension of GenericUserForm to handle theme-specific HTML attributes """

    class Meta(cforms.GenericUserForm.Meta):
        model = ScaplUser


class ScaplUserCreationForm(ThemeSpecificMixin, cforms.GenericUserCreationForm):
    """ An extension of ScaplUserUpdateForm and GenericUserCreationForm to handle theme-specific HTML attributes and duplicate emails """

    class Meta(cforms.GenericUserForm.Meta):
        model = ScaplUser

    def __init__(self, *args, **kwargs):
        super(ScaplUserCreationForm, self).__init__(*args, **kwargs)
        # 'email' is disabled on the profile page and is then not passed ; this line fixes it
        del self.fields['email'].widget.attrs['disabled']
        self.fields['new_password1'].required = True
        self.fields['new_password2'].required = True
