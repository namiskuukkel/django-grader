from django.db import models
from course_management.models import Assignment
from django.contrib.auth.models import User

class TestResult(models.Model):
    assignment_name = course = models.ForeignKey(Assignment, related_name='assignment_name')
    user = models.ForeignKey(User, related_name='user')
    score = models.SmallIntegerField()
    max_score = models.SmallIntegerField()
    student_result = models.TextField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Snippet(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at', )