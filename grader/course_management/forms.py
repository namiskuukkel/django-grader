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

    def slash_check(self):
        student_dir = self.cleaned_data['student_code_dir']
        logging.info("dir:" +  student_dir)
        if student_dir[:-1] != '/':
            self.cleaned_data['student_code_dir'] = student_dir + '/'
            logging.info("dir:" +  self.cleaned_data['student_code_dir'])

        assignment_dir = self.cleaned_data['assignment_base_dir']
        if assignment_dir[:-1] != '/':
            self.cleaned_data['assignment_base_dir'] = assignment_dir + '/'

class AssignmentForm(ModelForm):
    class Meta:
        model = Assignment
        fields = '__all__'

