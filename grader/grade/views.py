#!/usr/bin/python
# -*- coding: UTF-8 -*-

from .forms import EditorForm
from course_management.models import Assignment, Course, UserAttempts
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .utils import *
from .test_tools import *
import sys
import imp
logging.basicConfig(filename='/var/log/grader/grader.log', level=logging.DEBUG)

template = "An exception of type {0} occured. Arguments:\n{1!r}"

@login_required
def code(request):
    message = ""
    error_message = ""

    if not 'outcome' in request.session or not 'course_name' in request.session \
            or not 'assignment_name' in request.session:
        #This error message should be as it is, as the site can't load properly without these parameters
        return HttpResponse("Missing parameters")

    # Fetch the object matching the assignment name given by the LTI
    assignment_name = request.session['assignment_name']
    course_name = request.session['course_name']

    try:
        assignment = Assignment.objects.get(name=assignment_name, course__name=request.session['course_name'])
    except Assignment.DoesNotExist:
        logging.warning('Assignment not found: ' + assignment_name)
        #This error message should be as it is, as the site can't load properly without this parameter
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
            save_code(course_name, assignment_name, request.user.username, form.cleaned_data['text'])
            #docker run -v <volume: folder shared with docker container> --net='none' <no networking> -m <amount of memory to use> --rm='true'
            #-m not working on Ubuntu: p = subprocess.Popen(['docker', 'run', '--volume', '/root:/test', '--net', 'none', '--rm',
            # '-m', '50m', 'student_test', 'to_test.py', 'test'])
            result = build_docker("student")
            if result != "ok":
                error_message = result
            try:
                code_dir = Course.objects.get(name=course_name).student_code_dir + assignment_name.replace(" ","_") + \
                           '/' + request.user.username + '/'
                logging.info(code_dir)
                out = open(code_dir + 'result.txt', 'w+')
                err = open(code_dir + 'error.txt', 'w+')
                timeout = Assignment.objects.get(name=assignment_name, course__name=course_name).execution_timeout
                #subprocess.call(["cp", "/home/docker/Student-Docker/run-entrypoint.sh", code_dir])
            except Exception as e:
                logging.error( template.format(type(e).__name__, e.args))
                redirect('error')

            if run(code_dir, "student_run", out, err, timeout):
                #Close and open again for reading (some errors appeared with wr)
                #TODO: testaa uudestaan toimiiko
                out.close()
                err.close()
                out = open(code_dir + 'result.txt', 'r')
                err = open(code_dir + 'error.txt', 'r')
                #Should have something in either of these
                if not is_empty(out):
                    message = out.read()
                else:
                    if not is_empty(err):
                        error = err.read()
                    else:
                        return HttpResponse("Oops! You shouldn't have gotten here!")
            else:
                error_message = "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."
            out.close()
            err.close()
            #return redirect('/')
    else:
        form = EditorForm()
        code_file = Course.objects.get(name=course_name).student_code_dir + '/' + assignment_name +\
                    '/' + request.user.username + '/student_code.py'
        if os.path.isfile(code_file):
            f = open(code_file, 'r')
            form.text = f.read()

    return render(request, "grade/editor.html",
                  {
                    "form": form,
                    "user": request.user,
                    "course": course_name,
                    "assignment": assignment,
                    "now": datetime.now(),
                    "message": message,
                    "error": error_message,
                    "attempts_left": attempts_left,
                  })


@login_required
def grade(request):
    if request.method == 'POST':
        form = EditorForm(request.POST)
        message = ""
        error_message = ""
        assignment_name = request.session['assignment_name']
        course_name = request.session['course_name']
        attempts_left = 0
        try:
            assignment = Assignment.objects.get(name=assignment_name, course__name=request.session['course_name'])
        except Exception as e:
            logging.error(template.format(type(e).__name__, e.args))
            redirect('error')

        if assignment.attempts > 0:
            try:
                user_attempts = UserAttempts.objects.get(user__username=request.user.username,
                                                         assignment__id=assignment.id)
                #One attempt has been used
                attempts_left = user_attempts.attempts
                if attempts_left == 0:
                    return HttpResponse("Olet jo käyttänyt kaikki yrityskertasi")

            except Exception as e:
                logging.error(template.format(type(e).__name__, e.args))
                redirect('error')

        if form.is_valid():
            #Save on valid form submission
            save_code(course_name, assignment_name, request.user.username, form.cleaned_data['text'])

            code_dir = Course.objects.get(name=course_name).student_code_dir + assignment_name + '/'\
                       + request.user.username
            # Copy test files from assignment directory to the shared volume
            subprocess.call(["cp", Course.objects.get(name=request.session['course_name']).assignment_base_dir + "/"
                             + request.session['assignment_name'] + "/*", code_dir])
            #Copy the entrypoint for docker to the shared volume
            #subprocess.call(["cp", "/home/docker/Example-docker/grader-entrypoint.sh", code_dir])
            description = imp.load_source(code_dir + 'description')

            result = open(code_dir + 'test_result.txt', 'w')
            for test in description.tests:
                result.write(test["name"])
                result.write(test["description"])
                if test["type"] == "compare_output":
                    test_result = diff_test(test, code_dir, result)
                    if test_result["pass"] == "error":
                        redirect('error')
                    elif test_result["pass"] == "pass":
                        result.write(test["points"])
                        #If assignment.attempts > 0, then the number of attempts is limited
                        if assignment.attempts > 0:
                            try:
                                user_attempts = UserAttempts.objects.get(user__username=request.user.username,
                                                                         assignment__id=assignment.id)
                                #One attempt has been used
                                user_attempts.attempts = user_attempts - 1
                                user_attempts.save()
                            except Exception as e:
                                logging.error(template.format(type(e).__name__, e.args))
                                redirect('error')

            return render(request, "grade/results.html",
                  {
                    "form": form,
                    "user": request.user,
                    "course": course_name,
                    "assignment_name": assignment_name,
                    "now": datetime.now(),
                    "message": message,
                    "error": error_message,
                    "attempts_left": attempts_left
                  })


def error(request):
    return render(request, "grade/error.html")

def index(request):
    return HttpResponse("Tulit tänne suoraan kulkematta Canvas ruudun kautta")