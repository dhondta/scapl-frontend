from django.conf.urls import patterns, url
from .views import start_wizard


urlpatterns = [
    url(r'^(?P<apl_id>.+)?(/?P<seq_id>.+)?$', start_wizard, name='wizard'),
]
