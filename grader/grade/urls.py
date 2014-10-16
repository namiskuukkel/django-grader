#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'/grade/$', views.grade, name='grade'),
    url(r'$', views.code, name='code'),
)