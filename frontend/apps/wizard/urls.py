from django.conf.urls import url
from .views import list_reports, list_tasks, start_wizard, save_data_item, trigger_data_item


urlpatterns = [
    url(r'^wizard/$', start_wizard, name='wizard'),
    url(r'^wizard/(?P<apl_id>[0-9]+)/$', start_wizard, name='wizard'),
    url(r'^wizard/(?P<apl_id>[0-9]*)/(?P<seq_id>[0-9]*)/$', start_wizard, name='wizard'),
    url(r'^save/$', save_data_item, name='save_di'),
    url(r'^trigger/$', trigger_data_item, name='trigger_di'),
    url(r'^trigger/(?P<task_id>[0-9]+\-[0-9]+)/$', trigger_data_item, name='trigger_di'),
    url(r'^tasks/$', list_tasks, name='tasks'),
    url(r'^reports/$', list_reports, name='reports'),
]
