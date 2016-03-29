# -*- coding: UTF-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import APLTask, APLTaskItem


SAMPLE_KEYWORDS = (
    ('1', 'adobe,acrobat,reader,11', ),
    ('2', 'ccleaner,5', ),
    ('3', 'vlc,media,player,2.2.2', ),
    ('4', 'winrar,5.31', ),
    ('5', 'skype,7.21', ),
)


class ThemeSpecificMixin(object):
    """ A mix-in for handling theme-specific HTML attributes """

    def __init__(self, *args, **kwargs):
        title = kwargs.pop('title', None)
        super(ThemeSpecificMixin, self).__init__(*args, **kwargs)
        self.form_title = _(title or "Create an APL")
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
            # add 'autocomplete' attribute for all fields
            self.fields[field].widget.attrs['autocomplete'] = 'off'


class APLTaskInitStepForm(ThemeSpecificMixin, forms.ModelForm):
    """ A form handling the first step of an APL task sequence """
    keywords = forms.ChoiceField(widget=forms.Select, choices=SAMPLE_KEYWORDS)
    packages = forms.FileField(required=False)

    class Meta:
        model = APLTask
        fields = ('keywords', 'packages', )

    def clean_keywords(self):
        keywords = self.cleaned_data['keywords']
        # TODO: handle keywords as tags and validate if keywords together match an existing software product
        return keywords

    def save(self, commit=True, **kwargs):
        request = kwargs.pop('request', None)
        task = super(APLTaskInitStepForm, self).save(commit=False)
        task.author = request.user
        if commit:
            task.save()
        return task


class APLTaskItemForm(ThemeSpecificMixin, forms.ModelForm):
    """ A form handling an APL task item """

    class Meta:
        model = APLTaskItem
        fields = ('apl', 'item', 'value', )


class APLTaskSequenceSelectionForm(ThemeSpecificMixin, forms.Form):
    """ A form handling the first step of an APL task sequence """
    sequence = forms.ChoiceField(choices=(), label=_('Sequence'))

    def __init__(self, *args, **kwargs):
        self.sequences = kwargs.pop('choices')
        super(APLTaskSequenceSelectionForm, self).__init__(*args, **kwargs)
        choices = []
        for i, seq_obj in enumerate(self.sequences):
            choices.append((u'{}'.format(i), seq_obj.name, ))
        self.fields['sequence'].choices = tuple(choices)
