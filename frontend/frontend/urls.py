from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

admin.site.site_title = _('SCAPL Frontend')
admin.site.site_header = _('SCAPL Administration')
admin.site.index_title = _('SCAPL-FE Internals Management')

admin.autodiscover()
admin.site.login = login_required(admin.site.login)

urlpatterns = [
    url(r'^admin/', include('smuggler.urls')),  # before admin url patterns!
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('apps.profiles.urls')),
    url(r'^wizard/', include('apps.wizard.urls')),
]
