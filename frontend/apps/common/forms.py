# -*- coding: UTF-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import GenericUser


class GenericUserUpdateForm(forms.ModelForm):
    """ A form handling user update with customized error messages and password confirmation """
    error_messages = {
        'duplicate_email': _("This email address already exists."),
        'password_mismatch': _("Both password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = GenericUser
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(GenericUserUpdateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_staff = True
        if commit:
            user.save()
        return user


class GenericUserForm(GenericUserUpdateForm):
    """ A form handling user creation with customized error messages, email validation and password confirmation """

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            GenericUser._default_manager.get(email=email)
        except GenericUser.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])
