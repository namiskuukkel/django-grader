from django.db import models
from django.contrib.auth.models import User
import os

class Course(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100)
    #Contact persons email for the case of emergengy
    contact = models.EmailField()
    #Settings
    student_code_dir = models.FilePathField(allow_folders=True, allow_files=False)
    assignment_base_dir = models.FilePathField(allow_folders=True, allow_files=False)
    use_gitlab = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id + ' ' + self.name)

class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, related_name='course')
    # 0 attempts allowed equals to infinite attempts
    attempts = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(editable=False)
    open_from = models.DateTimeField(blank=True)
    open_till = models.DateTimeField(blank=True)
    execution_timeout = models.PositiveIntegerField(default=15)

class UserAttempts(models.Model):
    user = models.ForeignKey(User)
    assignment = models.ForeignKey(Assignment)
    attempts = models.SmallIntegerField()