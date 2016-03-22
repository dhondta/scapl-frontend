# -*- coding: UTF-8 -*-
from django.conf.urls import url
from .views import home, password, profile, reports, signin, signout, signup


urlpatterns = [
    url(r'^$', signin, name='signin'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^signout/$', signout, name='signout'),
    url(r'^home/$', home, name='home'),
    url(r'^edit/$', profile, name='profile'),
    url(r'^reports/$', reports, name='reports'),
    url(r'^password/$', password, name='password'),
]
