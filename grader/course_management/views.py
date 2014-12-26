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

    if request.method == 'POST':
        if form.is_valid():
	    form = CourseForm(request.POST)
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
            return HttpResponse("Örrr")
        '''# Fetch from Canvas version
    if request.method == 'POST':
        form = CourseForm(request.POST)

        r = requests.get('https://mooc-dev.pit.cs.tut.fi/login/oauth2/auth',
                                headers={'client_id': client_id, 'response_type': 'code',
                                         'redirect_uri': redirect_uri})

        response = requests.get('https://canvas.instructure.com/api/v1/courses/' + id,
                                headers={'Authorization': 'Bearer ' + r['code']})

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
        return redirect('/manage/')'''

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
            assignment_name = form.cleaned_data['name'].replace(" ", "_")
            assignment_path = Course.objects.get(name=form.cleaned_data['course']).assignment_base_dir + assignment_name
            if not os.path.exists(assignment_path):
                os.makedirs(assignment_path)

            return redirect('/manage')
        else:
            return HttpResponse("Örrr")

    else:
        form = AssignmentForm()

    return render(request, "course_management/assignment.html", {
        "form": form,
        "user": request.user,
    })
