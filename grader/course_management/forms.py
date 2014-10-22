#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.forms import ModelForm
from .models import Assignment, Course
import logging

logging.basicConfig(filename='/var/log/grader/management.log',level=logging.DEBUG)
class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

class AssignmentForm(ModelForm):
    class Meta:
        model = Assignment
        fields = '__all__'

