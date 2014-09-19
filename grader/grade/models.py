from django.db import models
from LTI.models import LTIProfile

#
class Course(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return str(id)

class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course)
    # 0 attempts allowed equals to infinite attempts
    attempts = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(editable=False)

class UserAttempts(models.Model):
    user = models.ForeignKey(LTIProfile)
    attempts = models.SmallIntegerField()

class Snippet(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )