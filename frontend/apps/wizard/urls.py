from django.conf.urls import url
from .views import list_reports, list_tasks, start_wizard, save_data_item


urlpatterns = [
    url(r'^wizard/$', start_wizard, name='wizard'),
    url(r'^save/$', save_data_item, name='save_di'),
    url(r'^tasks/$', list_tasks, name='tasks'),
    url(r'^reports/$', list_reports, name='reports'),
]
