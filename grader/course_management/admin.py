from django.contrib import admin

# Register your models here.
from course_management.models import *

admin.site.register(UserAttempts)
admin.site.register(Course)
admin.site.register(Assignment)


