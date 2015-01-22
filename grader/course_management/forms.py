#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.forms import ModelForm
from .models import Assignment, Course, Parameter

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'


class AssignmentForm(ModelForm):
    class Meta:
        model = Assignment
        fields = '__all__'

class VariableForm(ModelForm):

    class Meta:
        model = Parameter
        fields = '__all__'