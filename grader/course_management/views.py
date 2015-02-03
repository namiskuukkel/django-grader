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
from grader.top_secret_canvas_client_settings import *
from django.core.urlresolvers import resolve

logging.basicConfig(filename='/var/log/grader/grader.log', level=logging.DEBUG)


@login_required
def manage(request):
    if not request.user.is_superuser:
        return PermissionDenied()

    # TODO: Change the course model to support some kind of user authentication on this listing
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

    course = ""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form = CourseForm(request.POST)
            form.save() 
            # Check if there is an ending slash on the student code directory name
            # If not, add one and save that to database
            course = Course.objects.get(name=request.session['course_name'])
            student_dir = course.student_code_dir
            assignment_dir = course.assignment_base_dir
            if not student_dir[-1:] == '/':
                student_dir = student_dir + '/'
                course.student_code_dir = student_dir
                course.save()
            if not assignment_dir[-1:] == '/':
                assignment_dir = assignment_dir + '/'
                course.assignment_base_dir = assignment_dir
                course.save()
            return redirect('/manage/')
    else:
        course = None
        form = CourseForm()

    return render(request, "course_management/course.html", {
        "form": form,
        "user": request.user,
        "course": course,
    })

        # Fetch from Canvas version
'''@login_required
def add_course(request):
    if not request.user.is_superuser:
        return PermissionDenied()

    if request.method == 'POST':
        form = CourseForm(request.POST)

        #TODO: hardcoded
        r = requests.get('https://mooc.tut.fi/login/oauth2/auth',
                                headers={'client_id': 10000000000001 , 'response_type': 'code',
                                         'redirect_uri': resolve(request.path_info).url_name})
        token = "S49NA8uhdSErDKowppyGf2iNxmxply2xO4GKIhYyg0NNZtkycbMabX6VcHzwp86P"
        response = requests.get('https://mooc.tut.fi/api/v1/courses/1',
                                headers={'Authorization': 'Bearer ' + token})
        logging.debug(response)
        data = json.loads(response)
        course = data['name']
        to_add = Course()
        to_add.id = id
        to_add.name = course
        to_add.contact = request.POST['email']
        to_add.save()

        student_dir = course.student_code_dir
        assignment_dir = course.assignment_base_dir
        if not student_dir[-1:] == '/':
            student_dir = student_dir + '/'
            course.student_code_dir = student_dir
            course.save()
        if not assignment_dir[-1:] == '/':
            assignment_dir = assignment_dir + '/'
            course.assignment_base_dir = assignment_dir
            course.save()
        return redirect('/manage/')

    else:
        course = None
        form = CourseForm()

    return render(request, "course_management/course.html", {
        "form": form,
        "user": request.user,
        "course": course,
    })'''


@login_required
def add_assignment(request):
    if not request.user.is_superuser:
        return PermissionDenied()

    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        parameters = ""
        if form.is_valid():
            assignment_name = form.cleaned_data['name'].replace(" ", "_").encode("ascii", "ignore")
            assignment_path = Course.objects.get(name=form.cleaned_data['course']).assignment_base_dir + assignment_name
            if not os.path.exists(assignment_path):
                os.makedirs(assignment_path)

            form.save()
            return redirect('/manage/')
        else:
            return HttpResponse("Örrr")

    else:
        form = AssignmentForm()

    return render(request, "course_management/assignment.html", {
        "form": form,
        "user": request.user,
    })

def authenticate(request):
    if request.method == 'POST':
        return HttpResponse("Done")
    return render(request, "course_management/authenticator.html", {
    })
