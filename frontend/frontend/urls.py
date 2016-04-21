# -*- coding: UTF-8 -*-
from django.apps import apps
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from .decorators import admin_only, user_only, required

admin.site.site_title = _('SCAPL Frontend')
admin.site.site_header = _('SCAPL Administration')
admin.site.index_title = _('SCAPL-FE Internals Management')
admin.site.unregister(Site)

admin.autodiscover()

urlpatterns = [
    url(r'^', include('apps.profiles.urls')),
    url(r'^password/', apps.get_app_config('common').module.views.password, name='password'),
] + required(user_only, [
    url(r'^', include('apps.wizard.urls')),
    url(r'^summernote/', include('django_summernote.urls')),
]) + required(admin_only, [
    url(r'^dd5daef9ece2a85010e72a971ff35ea4/', include('smuggler.urls')),  # before admin url patterns!
    url(r'^dd5daef9ece2a85010e72a971ff35ea4/logout/', apps.get_app_config('profiles').module.views.signout),
    url(r'^dd5daef9ece2a85010e72a971ff35ea4/', include(admin.site.urls)),
])

if 'admin_honeypot' in settings.INSTALLED_APPS:
    urlpatterns.append(url(r'^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')))
