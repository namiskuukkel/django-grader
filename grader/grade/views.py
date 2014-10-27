#!/usr/bin/python
# -*- coding: UTF-8 -*-

from .forms import EditorForm
from course_management.models import Assignment, Course, UserAttempts
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .utils import *

logging.basicConfig(filename='/var/log/grader/grader.log', level=logging.DEBUG)

@login_required
def code(request):
    message = ""
    if not 'outcome' in request.session or not 'course_name' in request.session \
            or not 'assignment_name' in request.session:
        return HttpResponse("Missing parameters")

    # Fetch the object matching the assignment name given by the LTI
    assignment_name = request.session['assignment_name']
    course_name = request.session['course_name']

    try:
        assignment = Assignment.objects.get(name=assignment_name, course__name=request.session['course_name'])
    except Assignment.DoesNotExist:
        logging.warning('Assignment not found: ' + assignment_name)
        return HttpResponse("No assignment found!")

    attempts_left = 9999
    #If assignment.attempts > 0, then the number of attempts is limited
    if assignment.attempts > 0:
        try:
            user_attempts = UserAttempts.objects.get(user__username=request.user.username, assignment__id=assignment.id)
            attempts_left = user_attempts.attempts
        except UserAttempts.DoesNotExist:
            #User is trying this for the first time, create new db object that connects the user object to amount of
            #attempts the user has left to try this assignment
            to_add = UserAttempts()
            to_add.user = request.user
            to_add.assignment = assignment
            to_add.attempts = assignment.attempts
            attempts_left = assignment.attempts
            to_add.save()

    if request.method == 'POST':
        form = EditorForm(request.POST)
        if form.is_valid():
            save(course_name, assignment_name, request.user.username, form.cleaned_data['text'])
            #docker run -v <volume: folder shared with docker container> --net='none' <no networking> -m <amount of memory to use> --rm='true'
            #-m not working on Ubuntu: p = subprocess.Popen(['docker', 'run', '--volume', '/root:/test', '--net', 'none', '--rm',
            # '-m', '50m', 'student_test', 'to_test.py', 'test'])
            build_docker("run")
            try:
                code_dir = Course.objects.get(name=course_name).student_code_dir + assignment_name.replace(" ","_") +\
                           '/' + request.user.username + '/'
                logging.info(code_dir)
                out = open(code_dir + 'result.txt', 'w')
                err = open(code_dir + 'error.txt', 'w')
                logging.info(out)
                logging.info(err)
                timeout = Assignment.objects.get(name=assignment_name, course__name=course_name).execution_timeout
                subprocess.call(["cp", "/home/docker/Run-Docker/run-entrypoint.sh", code_dir])
                if run(code_dir, "student_run", out, err, timeout):
                    message = out.read() + '&' + err.read()
                else:
                    message = "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."
                out.close()
                err.close()
            except:
                return HttpResponse("Tapahtui virhe! Koodin ajaminen epäonnistui." \
                          "Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan")

        #return redirect('/')
    else:
        form = EditorForm()
        code_file = Course.objects.get(
            name=course_name).student_code_dir + '/' + assignment_name + '/' + request.user.username + '/to_test.py'
        if os.path.isfile(code_file):
            f = open(code_file, 'r')
            form.text = f.read()

    return render(request, "grade/editor.html", {
        "form": form,
        "user": request.user,
        "course": course_name,
        "assignment": assignment,
        "now": datetime.now(),
        "message": message,
        "attempts_left": attempts_left,
    })


@login_required
def grade(request):
    if request.method == 'POST':
        form = EditorForm(request.POST)
        message = ""
        assignment_name = request.session['assignment_name']
        course_name = request.session['course_name']
        if form.is_valid():

            #Save on valid form submission
            save(course_name, assignment_name, request.user.username, form.cleaned_data['text'])
            #Build docker image
            build_docker("grade")

            code_dir = Course.objects.get(name=course_name).student_code_dir + assignment_name + '/' + request.user.username
            # Copy test files from assignment directory to the shared volume
            subprocess.call(["cp", Course.objects.get(name=request.session['course_name']).assignment_base_dir + "/"
                     + request.session['assignment_name'] + "/*", code_dir])
            #Copy the entrypoint for docker to the shared volume
            subprocess.call(["cp", "/home/docker/Grade-Docker/grader-entrypoint.sh", code_dir])
            for test in code_dir.description.tests:
                try:
                    out = open(code_dir + test + '_result.txt', 'w')
                    err = open(code_dir + test+ '_error.txt', 'w')
                    logging.info(out)
                    logging.info(err)
                    timeout = Assignment.objects.get(name=assignment_name, course__name=course_name).execution_timeout
                    if run(code_dir, "student_grade", out, err, timeout):
                        message = out.read() + '&' + err.read()
                    else:
                        message = "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."
                    out.close()
                    err.close()
                except:
                    return HttpResponse("Tapahtui virhe! Koodin ajaminen epäonnistui." \
                            "Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan")

    redirect("/code")
