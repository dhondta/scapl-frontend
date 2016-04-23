# -*- coding: UTF-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteWidget, SummernoteInplaceWidget
from .models import Task, TaskItem


SAMPLE_KEYWORDS = (
    ('adobe,acrobat,reader,11', ) * 2,
    ('ccleaner,5', ) * 2,
    ('vlc,media,player,2.2.2', ) * 2,
    ('winrar,5.31', ) * 2,
    ('skype,7.21', ) * 2,
)


class BootstrapMixin(object):
    """ A mix-in for handling theme-specific HTML attributes """

    def __init__(self, *args, **kwargs):
        title = kwargs.pop('title', None)
        super(BootstrapMixin, self).__init__(*args, **kwargs)
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


class TaskInitStepForm(BootstrapMixin, forms.ModelForm):
    """ A form handling the first step of an APL task sequence """
    keywords = forms.ChoiceField(widget=forms.Select, choices=SAMPLE_KEYWORDS)
    packages = forms.FileField(required=False)

    class Meta:
        model = Task
        fields = ('keywords', 'packages', )

    def clean_keywords(self):
        keywords = self.cleaned_data['keywords']
        # TODO: handle keywords as tags and validate if keywords together match an existing software product
        return keywords

    def save(self, commit=True, **kwargs):
        request = kwargs.pop('request', None)
        task = super(TaskInitStepForm, self).save(commit=False)
        task.author = request.user
        if commit:
            task.save()
        return task


class MySummernoteWidget(SummernoteInplaceWidget):
    def render(self, name, value, attrs=None):
        # native Summernote widget only takes attrs from its __init__ whereas attrs is set during the wizard creation ;
        #  this avoids KeyError on 'id' because, in this implementation, attrs is None and self.attrs is to be used
        return super(MySummernoteWidget, self).render(name, value, attrs or self.attrs)


class TaskItemForm(forms.ModelForm):
    """ A form handling an APL task item """
    class Meta:
        model = TaskItem
        fields = ('apl', 'item', 'value', )
        widgets = {'value': MySummernoteWidget()}


class TaskSequenceSelectionForm(BootstrapMixin, forms.Form):
    """ A form handling the first step of an APL task sequence """
    sequence = forms.ChoiceField(choices=(), label=_('Sequence'))

    def __init__(self, *args, **kwargs):
        self.sequences = kwargs.pop('choices')
        super(TaskSequenceSelectionForm, self).__init__(*args, **kwargs)
        choices = []
        for i, seq_obj in enumerate(self.sequences):
            choices.append((u'{}'.format(i), seq_obj.name, ))
        self.fields['sequence'].choices = tuple(choices)
