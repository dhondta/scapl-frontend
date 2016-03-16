"""
FormWizard class -- implements a multi-page form, validating between each
step and storing the form's state as HTML hidden fields so that no state is
stored on the server side.

This is an extended version which allows display of multiple forms per step
"""

from django import forms
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.contrib.formtools.utils import security_hash

class MultiFormWizard(object):
    # The HTML (and POST data) field name for the "step" variable.
    step_field_name = "wizard_step"
    def __init__(self, **kwargs):
        """
        Changed __init__ method to suit our needs
        Takes a dictionary as first argument and abstracts from there the
        FormWizard's arguments
        @param kwargs: dict(
            forms = [ # List of dictionaries for each step
                dict(
                    form        = Form1,
                    linkform    = Form2,
                ), # Step 1
                dict(
                    textform    = Form3,
                ) # Step 2
            ],
            prefixes = [ # List of dictionaries for each step
                dict(
                    form     = 'main_form',
                    linkform = 'link_form',
                ),
                dict(
                    textform = 'text_form',
                )
            ],
            initial = [ # List of dictionaries with initial values for each step
                dict(
                    form     = None,
                    linkform = None,
                ),
                dict(
                    textform = None,
                )
            ],
            template = 'foo/bar.html'
        )
        """
        self.forms = kwargs.get('forms')
        self.prefixes = kwargs.get('prefixes', [])
        self.initial = kwargs.get('initial', [])
        self._build_initials()
        self.template = kwargs.get('template')
        self.extra_context = kwargs.get('extra_context', {})


    def _build_initials(self):
        """
        Builds the list with initial data to prevent IndexErrors in
        self.set_initial
        """
        for step, forms in enumerate(self.forms):
            try:
                init = self.initial[step]
            except IndexError:
                self.initial.append(dict())


    def set_inital(self, step, form_name, initial):
        self.initial[step][form_name] = initial

    def get_initials(self, step, form_name):
        """
        Return the initial data for a form
        """
        return self.initial[step].get(form_name)

    def get_prefix(self, step, form_name):
        """
        Returns the prefix for a form
        """
        try:
            prefixes = self.prefixes[step]
        except:
            prefixes = {}
        return u'%d_%s' % (
            step,
            prefixes.get(form_name)
        ) if prefixes.get(form_name) else  u'%d_%s' % (
            step,
            form_name
        )

    def get_forms(self, step, data = None, files = None):
        """
        Returns the forms for the given step
        """
        forms = dict()
        args = (data, files)

        for name, form in self.forms[step].iteritems():
            kwargs = dict()
            if hasattr(form, 'Meta') and hasattr(form.Meta, 'model'):
                init = 'instance'
            elif hasattr(form, 'management_form'):
                init = 'queryset'
            else:
                init = 'initial'

            kwargs.update({
                init : self.get_initials(step, name),
                'prefix' : self.get_prefix(step, name)
            })

            forms.update({name : form(*args, **kwargs)})

        return forms

    def num_steps(self):
        "Helper method that returns the number of steps."
        return len(self.forms)

    def __call__(self, request, *args, **kwargs):
        if kwargs.has_key('extra_context'):
            self.extra_context.update(kwargs.get('extra_context'))
        current_step = self.determine_step(request, *args, **kwargs)


        self.parse_params(request, *args, **kwargs)

        # sanity check
        if current_step >= self.num_steps():
            raise Http404('Step %s does not exist' % current_step)

        # For each previous step, verify the hash and process.
        # TODO: Move "hash_%d" to a method to make it configurable
        for step in range(current_step):
            forms = self.get_forms(step, request.POST)
            for name, form in forms.iteritems():
                form.full_clean()
                if request.POST.get('hash_%d_%s' % (step, name), '') != self.security_hash(request, form):
                    return self.render_hash_failure(request, step)

        # Process the current step. If it's valid, go to next step or done()
        if request.method == 'POST':
            forms = self.get_forms(current_step, request.POST, request.FILES)
        else:
            forms = self.get_forms(current_step)

        invalid = False

        for name, form in forms.iteritems():
            if not form.is_valid():
                invalid = True

        if not invalid:
            self.process_step(request, forms, current_step)
            next_step = current_step + 1

            # If this was the last step, validate all of the forms a last time
            # for sanity checking, then call done()
            steps = self.num_steps()
            if next_step == steps:
                final_form_list = [] # [ ( step, name, form ) , ... ]
                for step in range(steps):
                    for name in self.forms[step]:
                        final_form_list.append((
                            step, name, self.get_forms(step, request.POST, request.FILES).get(name)
                        ))
                for i, (step, name, form) in enumerate(final_form_list):
                    if not form.is_valid():
                        return self.render_revalidation_failure(request, step)

                return self.done(request, final_form_list)
            else:
                forms = self.get_forms(next_step)
                self.step = current_step = next_step

        return self.render(forms, request, current_step)

    def render(self, bound_forms, request, step, context = {}):
        "Renders the given Form object, returning an HttpResponse."
        old_data = request.POST
        prev_fields = []
        if old_data:
            hidden = forms.HiddenInput()
            # Collect all data from previous steps and render it as HTML hidden fields.
            for i in range(step):
                old_forms = self.get_forms(i, old_data)
                for name, form in old_forms.iteritems():
                    hash_name = u'hash_%d_%s' % (i, name)
                    prev_fields.extend(
                        [field.as_hidden() for field in form]
                    )
                    prev_fields.append(
                        hidden.render(
                            hash_name,
                            old_data.get(
                                hash_name,
                                self.security_hash(request, form)
                            )
                        )
                    )
        return self.render_template(request, bound_forms, ''.join(prev_fields), step, context)

    # METHODS SUBCLASSES MIGHT OVERRIDE IF APPROPRIATE ########################

    def render_hash_failure(self, request, step):
        """
        Hook for rendering a template if a hash check failed.

        step is the step that failed. Any previous step is guaranteed to be
        valid.

        This default implementation simply renders the form for the given step,
        but subclasses may want to display an error message, etc.
        """
        return self.render(
            self.get_forms(step),
            request,
            step,
            context = dict(
                wizard_error = _('We apologize, but your form has expired. Please continue filling out the form from this page.')
            )
        )

    def render_revalidation_failure(self, request, step):
        """
        Hook for rendering a template if final revalidation failed.

        It is highly unlikely that this point would ever be reached, but See
        the comment in __call__() for an explanation.
        """
        return self.render(
            self.get_forms(step, request.POST, request.FILES), request, step
        )

    def security_hash(self, request, form):
        """
        Calculates the security hash for the given HttpRequest and Form instances.

        Subclasses may want to take into account request-specific information,
        such as the IP address.
        """

        return security_hash(request, form)

    def determine_step(self, request, *args, **kwargs):
        """
        Given the request object and whatever *args and **kwargs were passed to
        __call__(), returns the current step (which is zero-based).

        Note that the result should not be trusted. It may even be a completely
        invalid number. It's not the job of this method to validate it.
        """
        if not request.POST:
            return 0
        try:
            step = int(request.POST.get(self.step_field_name, 0))
        except ValueError:
            return 0
        return step

    def parse_params(self, request, *args, **kwargs):
        """
        Hook for setting some state, given the request object and whatever
        *args and **kwargs were passed to __call__(), sets some state.

        This is called at the beginning of __call__().
        """
        pass

    def get_template(self, step):
        """
        Hook for specifying the name of the template to use for a given step.

        Note that this can return a tuple of template names if you'd like to
        use the template system's select_template() hook.
        """
        if not self.template:
            raise ValueError, 'Please provide a template'
        return self.template

    def render_template(self, request, forms, previous_fields, step, context = {}):
        """
        Renders the template for the given step, returning an HttpResponse object.

        Override this method if you want to add a custom context, return a
        different MIME type, etc. If you only need to override the template
        name, use get_template() instead.

        The template will be rendered with the following context:
            step_field -- The name of the hidden field containing the step.
            step0      -- The current step (zero-based).
            step       -- The current step (one-based).
            step_count -- The total number of steps.
            form       -- The Form instance for the current step (either empty
                          or with errors).
            previous_fields -- A string representing every previous data field,
                          plus hashes for completed forms, all in the form of
                          hidden fields. Note that you'll need to run this
                          through the "safe" template filter, to prevent
                          auto - escaping, because it's raw HTML.
        """
        context = context or {}
        context.update(self.extra_context)
        return render_to_response(self.get_template(step), dict(context,
            step_field = self.step_field_name,
            step0 = step,
            step = step + 1,
            step_count = self.num_steps(),
            forms = forms,
            previous_fields = previous_fields
        ), context_instance = RequestContext(request))

    def process_step(self, request, forms, step):
        """
        Hook for modifying the FormWizard's internal state, given a fully
        validated Form object. The Form is guaranteed to have clean, valid
        data.

        This method should * not * modify any of that data. Rather, it might want
        to set self.extra_context or dynamically alter self.form_list, based on
        previously submitted forms.

        Note that this method is called every time a page is rendered for * all *
        submitted steps.
        """
        pass

    # METHODS SUBCLASSES MUST OVERRIDE ########################################

    def done(self, request, form_list):
        """
        Hook for doing something with the validated data. This is responsible
        for the final processing.

        form_list is a list of Form instances, each containing clean, valid
        data.
        """
        raise NotImplementedError("Your %s class has not defined a done() method, which is required." % self.__class__.__name__)
