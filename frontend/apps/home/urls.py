from django.conf.urls import patterns, url
from django.conf.urls import include, url
from django.contrib import admin
from .views import home
admin.autodiscover()

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^(?P<apl_id>.+)?(/?P<seq_id>.+)?$', start_wizard, name='wizard'),
]
