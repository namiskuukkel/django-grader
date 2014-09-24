from django.shortcuts import render

from course_management.models import *
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import requests
from django.contrib.auth.decorators import login_required
import json

@login_required
def add_course(request):

    if not request.user.is_superuser():
        return PermissionDenied()

    if request.method == 'POST':
        id = request.POST['course_id']
        if not id:
            return HttpResponse("No course id provided!")
        elif not request.POST['email']:
            return HttpResponse("No contact email provided!")

        response = requests.get('https://canvas.instructure.com/api/v1/courses/' + id)
        data = json.loads(response)
        course = data['name']
        to_add = Course()
        to_add.id = id
        to_add.name = course
        to_add.contact = request.POST['email']
        return redirect('/')
    else:
        course = None

    return render(request, "course_management/add_course.html", {
        "user": request.user,
        "course": course,
    })
