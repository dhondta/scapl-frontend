from django.conf.urls import include, url
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

admin.site.site_title = 'SCAPL Frontend'
admin.site.site_header = _('SCAPL Administration')
admin.site.index_title = 'SCAPL-FE Internals Management'

urlpatterns = [
    url(r'^admin/', include('smuggler.urls')),  # before admin url patterns!
    url(r'^admin/', include(admin.site.urls)),
    url(r'^wizard/', include('apps.wizard.urls')),
    url(r'^home/', include('apps.home.urls')),
]
