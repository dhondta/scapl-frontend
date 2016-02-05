# -*- coding: UTF-8 -*-
from django import forms
from django.apps import apps
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

user_app, user_model = settings.AUTH_USER_MODEL.split('.')


class AdminsitratorAddForm(forms.ModelForm):
    """ A form that creates a user, with privileges, from the given email and password """
    error_messages = {
        'duplicate_email': _("This email address already exists."),
        'password_mismatch': _("Both password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = apps.get_app_config(user_app).get_model(user_model)
        fields = ('email', )

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            self.model._default_manager.get(email=email)
        except self.model.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(AdminsitratorAddForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_staff = True
        if commit:
            user.save()
        return user


class AdminsitratorUpdateForm(AdminsitratorAddForm):
    """ A form to update user's data, based on the add form """
    pass
