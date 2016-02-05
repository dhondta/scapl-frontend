# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _


class Title(models.Model):
    """ This model handles user's titles """
    short = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=60, unique=True)


class Rank(models.Model):
    """ This model handles user's ranks """
    short = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=60, unique=True)


class Country(models.Model):
    """ This model handles countries for use with localities """
    label = models.CharField(max_length=60, default="Belgium", unique=True)

    def __unicode__(self):
        return self.label


class Locality(models.Model):
    """ This model handles localities for use with addresses """
    label = models.CharField(max_length=60, default="Brussels")
    postal_code = models.CharField(max_length=6, db_index=True)
    country = models.ForeignKey(Country, default=1, related_name="locality_country")

    class Meta:
        unique_together = ('label', 'postal_code', 'country')

    def __unicode__(self):
        return u"{}-{}".format(self.postal_code, self.label)


class Address(models.Model):
    """ This model handles addresses for use with departments """
    street = models.CharField(max_length=100, default=None, blank=True, null=True)
    number = models.CharField(max_length=6, default=None, blank=True, null=True)
    locality = models.ForeignKey(Locality, default=None, blank=True, null=True, related_name="addresses")


class Element(models.Model):
    """ This generic model handles the base information of an organization's element """
    name = models.CharField(max_length=60, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True)

    class Meta:
        abstract = True


class OrganizationalUnit(Element):
    """ This model handles organizational units for use with departments """
    def __str__(self):
        return u'{}'.format(self.abbreviation)


class Department(Element):
    """ This model handles departments for use with services """
    organization = models.ForeignKey(OrganizationalUnit, related_name="departments")

    def __str__(self):
        return u'{}/{}'.format(str(self.organization), self.abbreviation)


class Service(Element):
    """ This model handles user's services """
    department = models.ForeignKey(Department, related_name="services")

    def __str__(self):
        return u'{}/{}'.format(str(self.department), self.abbreviation)


class GenericUserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(email=email, is_superuser=False, last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        return None


class GenericUser(AbstractBaseUser, PermissionsMixin):
    """ This model defines a new generic user with additional fields compared to auth module's User model
     using the email as the authentication data """
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    title = models.ForeignKey(Title, default=None, blank=True, null=True, related_name="users")
    rank = models.ForeignKey(Rank, default=None, blank=True, null=True, related_name="users")
    service = models.ForeignKey(Service, default=None, blank=True, null=True, related_name="users")
    phone1 = models.CharField(max_length=30, default=None, blank=True, null=True)
    phone2 = models.CharField(max_length=30, default=None, blank=True, null=True)
    comments = models.TextField(max_length=1000, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = GenericUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELD = ('email', 'first_name', 'last_name', )

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])
