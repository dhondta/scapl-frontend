from django.conf.urls import url
from .views import start_wizard


urlpatterns = [
    url(r'^$', start_wizard, name='wizard'),
]
