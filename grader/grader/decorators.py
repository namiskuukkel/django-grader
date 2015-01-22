# -*- coding: utf-8 -*-

import httplib

from functools import wraps
from django.http import HttpResponse


def session_data(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not 'outcome' in request.session or not 'course_name' in request.session \
                or not 'assignment_name' in request.session:
            #This error message should be as it is, as the site can't load properly without these parameters
            return HttpResponse("Missing parameters")
        return wrapper