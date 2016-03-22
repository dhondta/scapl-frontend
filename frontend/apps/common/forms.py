# -*- coding: UTF-8 -*-
from django import forms
from django.forms.widgets import Select
from django.utils.translation import ugettext_lazy as _
from .models import GenericUser, Title, Rank, Service


class GenericUserForm(forms.ModelForm):
    """ A form handling user base update and creation functionalities with customized error messages and password confirmation """
    error_messages = {
        'duplicate_email': _("This email address already exists"),
        'password_mismatch': _("Both password fields didn't match"),
        'bad_old_password': _("Bad old password"),
    }
    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput)
    title = forms.ModelChoiceField(queryset=Title.objects.all(), empty_label=_("Title"))
    rank = forms.ModelChoiceField(queryset=Rank.objects.all(), empty_label=_("Rank"))
    service = forms.ModelChoiceField(queryset=Service.objects.all(), empty_label=_("Service"))

    class Meta:
        model = GenericUser
        fields = ('email', 'first_name', 'last_name', 'title', 'rank', 'service', 'phone1', 'phone2', )
        labels = {
            'email': _('E-mail'),
            'phone1': _('Professional phone'),
            'phone2': _('Personal phone'),
        }

    def __init__(self, *args, **kwargs):
        super(GenericUserForm, self).__init__(*args, **kwargs)
        for field in set(self.Meta.fields) - set(self.Meta.labels.keys()):
            self.Meta.labels[field] = _(field.capitalize().replace("_", " "))
        # 'email' is disabled on the profile page and is then not passed ; this line fixes it
        for field in ['title', 'rank', 'service']:
            self.fields[field].empty_label = self.Meta.labels[field]

    def clean_password2(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'])
        return new_password2

    def save(self, commit=True):
        user = super(GenericUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user


class GenericUserUpdateForm(GenericUserForm):
    """ A form fully handling user update with customized error messages, old password and new password confirmation """
    old_password = forms.CharField(label=_("Old password"), widget=forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        super(GenericUserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.value_from_datadict = lambda *args: self.instance.email
        self.fields['new_password1'].required = False
        self.fields['new_password2'].required = False

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.instance.check_password(old_password):
            raise forms.ValidationError(self.error_messages['bad_old_password'])
        return old_password

    def save(self, commit=True):
        user = super(GenericUserUpdateForm, self).save(commit=False)
        old_password = self.cleaned_data.get('old_password')
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')
        user.set_password(new_password1 if new_password1 == new_password2 != "" else old_password)
        if commit:
            user.save()
        return user


class GenericUserCreationForm(GenericUserForm):
    """ A form handling user creation with customized error messages, email validation and password confirmation """

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            GenericUser._default_manager.get(email=email)
        except GenericUser.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])
