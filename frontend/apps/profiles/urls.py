# -*- coding: UTF-8 -*-
from django.conf.urls import url
from frontend.decorators import anonymous_only, user_only
from .views import home, password, profile, signin_or_signup, signout


urlpatterns = [
    url(r'^$', signin_or_signup, name='index'),
    url(r'^signout/$', user_only(signout), name='signout'),
    url(r'^home/$', user_only(home), name='home'),
    url(r'^edit/$', user_only(profile), name='profile'),
    url(r'^password/$', anonymous_only(password), name='password'),
]
