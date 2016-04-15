# -*- coding: UTF-8 -*-
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import now
from importlib import import_module

pmodels = import_module("apps.profiles.models")
smodels = import_module("apps.scheme.models")


class GenericBackend(ModelBackend):
    """ Generic class to handle 'user_class' property creation using the ScaplUser model from the 'profiles' app. """

    def get_user(self, user_id):
        try:
            return self.user_model.objects.get(pk=user_id)
        except self.user_model.DoesNotExist:
            return None

    @property
    def user_model(self):
        if not hasattr(self, '_user_model'):
            self._user_model = pmodels.ScaplUser
            if not self._user_model:
                raise ImproperlyConfigured('Could not get custom user model')
        return self._user_model


class GenericUserBackend(GenericBackend):
    """ Authenticate using the ScaplUser model from the 'profiles' app. """

    def authenticate(self, username=None, password=None, **kwargs):
        email = username or kwargs.get(self.user_model.USERNAME_FIELD)
        try:
            user = self.user_model.objects.get(email=email)
            if user.check_password(password):
                return user
        except self.user_model.DoesNotExist:
            return None


class SuperUserCreationBackend(GenericBackend):
    """ Authenticate against the settings ADMIN_EMAIL and ADMIN_PASSWORD and create the admin if it doesn't exist. """

    @property
    def admin_model(self):
        if not hasattr(self, '_admin_model'):
            self._admin_model = smodels.Administrator
            if not self._admin_model:
                raise ImproperlyConfigured('Could not get custom administrator model')
        return self._admin_model

    def authenticate(self, username=None, password=None, **kwargs):
        email = username or kwargs.get(self.admin_model.USERNAME_FIELD)
        if settings.ADMIN_EMAIL == email and check_password(password, settings.ADMIN_PASSWORD):
            try:
                admin = self.admin_model.objects.get(email=email)
            except self.admin_model.DoesNotExist:
                admin = self.admin_model(email=email, password=settings.ADMIN_PASSWORD)
                admin.type = 2
                admin.is_active = True
                admin.is_staff = True
                admin.is_superuser = True
                admin.is_email_verified = True
                admin.last_login = now()
                admin.save()
            return admin
        return None
