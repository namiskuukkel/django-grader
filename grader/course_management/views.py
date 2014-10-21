#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.shortcuts import render

from .models import Course, Assignment
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
import requests
from django.contrib.auth.decorators import login_required
import json
from .forms import *
import os
import logging

logging.basicConfig(filename='/var/log/grader/management.log',level=logging.DEBUG)

@login_required
def manage(request):
    if not request.user.is_superuser:
        return PermissionDenied()

    #TODO: Change the course model to support some kind of user authentication on this listing
    courses = Course.objects.all()
    assignments = Assignment.objects.all()
    return render(request, "course_management/management.html", {
        "courses": courses,
        "assignments": assignments
    })

@login_required
def add_course(request):

    if not request.user.is_superuser:
        return PermissionDenied()

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['student_code_dir'].endswith('/'):
                form.cleaned_data['student_code_dir'] = form.cleaned_data['student_code_dir'] + '/'
            if not form.cleaned_data['assignment_base_dir'].endswith('/'):
                form.cleaned_data['assignment_base_dir'] = form.cleaned_data['assignment_base_dir'] + '/'
            form.save()
            return HttpResponse("Success!")
        else:
            return HttpResponse("Örrr")
        #Fetch from Canvas version
        '''id = request.POST['course_id']
        if not id:
            return HttpResponse("No course id provided!")
        elif not request.POST['email']:
            return HttpResponse("No contact email provided!")

        response = requests.get('https://canvas.instructure.com/api/v1/courses/' + id)
        return HttpResponse(response)

        data = json.loads(response)
        course = data['name']
        to_add = Course()
        to_add.id = id
        to_add.name = course
        to_add.contact = request.POST['email']
        return redirect('/')'''
    else:
        course = None
        form = CourseForm()

    return render(request, "course_management/course.html", {
        "form": form,
        "user": request.user,
        "course": course,
    })

@login_required
def add_assignment(request):
    if not request.user.is_superuser:
        return PermissionDenied()

    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            assignment_path = Course.objects.get(name = form.cleaned_data['course']).assignment_base_dir + "/"
            + form.cleaned_data['name']
            if not os.path.exists(assignment_path):
                    try:
                        os.makedirs(assignment_path)
                    except:
                        logging.info("Failed to create:" + assignment_path)
            return HttpResponse("Success!")
        else:
            return HttpResponse("Örrr")

    else:
        form = AssignmentForm()

    return render(request, "course_management/assignment.html", {
        "form": form,
        "user": request.user,
    })
