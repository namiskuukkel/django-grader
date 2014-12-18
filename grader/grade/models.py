#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.db import models
from course_management.models import Assignment
from django.contrib.auth.models import User

#TODO: Siirrä näitä testi olioihin
class TestResult(models.Model):
    assignment_name = models.ForeignKey(Assignment, related_name='assignment_name')
    type = models.TextField()
    test_name = models.TextField()
    description = models.TextField()
    user = models.ForeignKey(User, related_name='user')
    student_result = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class NumericResult(TestResult):
    score = models.SmallIntegerField()
    max_score = models.SmallIntegerField()

class BinaryResult(TestResult):
    passed = models.BooleanField()

class Snippet(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )