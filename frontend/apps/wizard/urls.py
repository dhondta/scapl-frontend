from django.conf.urls import url
from .views import start_wizard, save_data_item


urlpatterns = [
    url(r'^$', start_wizard, name='wizard'),
    url(r'^save/$', save_data_item, name='save_di'),
]
