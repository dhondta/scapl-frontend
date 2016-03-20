from django.conf.urls import url

from .views import home, index, profile, registration

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^home/$', home, name='home'),
    url(r'^profile/$', profile, name='profile'),
    url(r'^registration/$', registration, name='registration'),
]
