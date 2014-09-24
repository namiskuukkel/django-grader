from django.db import models
from LTI.models import LTIProfile

class Course(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100)
    #Contact persons email for the case of emergengy
    contact = models.EmailField(blank=True)

    def __str__(self):
        return str(id)

class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, related_name='course')
    # 0 attempts allowed equals to infinite attempts
    attempts = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(editable=False)
    open_from = models.DateTimeField(blank=True)
    open_till = models.DateTimeField(blank=True)

class UserAttempts(models.Model):
    user = models.ForeignKey(LTIProfile)
    attempts = models.SmallIntegerField()