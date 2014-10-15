from django.forms import ModelForm
from .models import Assignment, Course

class CourseForm(ModelForm):
    fields = ['id', 'name', 'contact']
    class Meta:
        model = Course


class AssignmentForm(ModelForm):
    fields = ['name', 'course', 'attempts', 'description', 'open_from', 'open_till', 'execution_timeout']
    class Meta:
        model = Assignment

