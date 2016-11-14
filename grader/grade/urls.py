#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.conf.urls import  url
from views import grade, code, error, index

urlpatterns = [
    url(r'grade/', grade, name='grade'),
    url(r'code/', code, name='code'),
    url(r'error/',error, name='error'),
    url(r'$', index, name='index'),
]
