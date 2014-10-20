#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    id = models.CharField(max_length=30, primary_key=True, help_text="ID is found on course's Canvas URL")
    name = models.CharField(max_length=100)
    #Contact person's email for the case of emergengy
    contact = models.EmailField()
    #Settings
    student_code_dir = models.CharField(blank=True, max_length=300, verbose_name="Student Code Base Directory")
    assignment_base_dir = models.CharField(blank=True, max_length=300, verbose_name="Assignment Base Directory")
    use_gitlab = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id + ' ' + self.name)

class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, related_name='course')
    # 0 attempts allowed equals to infinite attempts
    attempts = models.PositiveSmallIntegerField(default=0)
    description = models.TextField()
    open_from = models.DateTimeField(blank=True)
    open_till = models.DateTimeField(blank=True)
    execution_timeout = models.PositiveIntegerField(default=15)

class UserAttempts(models.Model):
    user = models.ForeignKey(User, related_name='user')
    assignment = models.ForeignKey(Assignment, related_name='assignment')
    attempts = models.SmallIntegerField()