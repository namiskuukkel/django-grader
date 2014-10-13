from .forms import EditorForm
from coursemanagement.models import *
import coursemanagement.course_settings
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.files import File
import subprocess
import os

@login_required
def grade(request, course_name, assignment_name):

    if not 'course_id' in request.session or not 'outcome' in request.session:
        return HttpResponse("Missing parameters")

    #Fetch the object matching the assignment name given by the LTI
    #TODO: match coursename also!
    '''try:
        assignment = Assignment.objects.get(name = assignment_name)
    except Assignment.DoesNotExist:
        return HttpResponse("No assignment found!")

    #The name given had multiple hits in the database
    if assignment.count > 1:
        return HttpResponse("Too many assignments found!")

    attempts_left = 9999
    if assignment.attempts > 0:
        user_attempts = UserAttempts.objects.get(user__name=request.user.username)
        if user_attempts.count == 0:
            to_add = UserAttempts()
            to_add.user = request.user.id
            to_add.attempts = assignment.attempts
            attempts_left = assignment.attempts
            to_add.save()
        elif assignment.count > 1:
            return HttpResponse("Too many results found!")
    '''
    request.session['assignment'] = assignment_name
    request.session['course'] = course_name
    if request.method == 'POST':
        form = EditorForm(request.POST)
        if form.is_valid():
            tmp_dir = coursemanagement.course_settings.student_code_dir + "tmp_" + request.user.username
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            f = open(tmp_dir + "/test.py", 'w')
            myfile = File(f)
            myfile.write(form.cleaned_data['text'])
            out = open("result","w")
            p = subprocess.Popen(['docker', 'run', 'test_runner', '-v', tmp_dir + "/test.py:/student.py",  '--ip-forward', 'false', '-m', '50m'], stdout=out)
            while p.poll():
        return redirect('/')
    else:
        form = EditorForm()
        #TODO: user attempts!
    return render(request, "grade/editor.html", {
        "form": form,
        "user": request.user,
        "course": course_name,
        #"assignment": assignment,
        "now": datetime.now(),
        #"attempts_left": attempts_left,
    })
