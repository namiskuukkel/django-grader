#!/usr/bin/python
# -*- coding: UTF-8 -*-

from .forms import EditorForm, DoubleEditorForm
from course_management.models import Assignment, Course, UserAttempts
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
 import httplib2
from .utils import *
from .test_tools import *
from .models import *
from grader.decorators import session_data
from docker_settings import *
import sys
import imp
from django.forms.formsets import formset_factory
logging.basicConfig(filename='/var/log/grader/grader.log', level=logging.DEBUG)

template = "An exception of type {0} occured. Arguments:\n{1!r}"

@login_required
@session_data
def code(request):
    message = ""
    error_message = ""

    # Fetch the object matching the assignment name given by the LTI
    assignment_name = request.session['assignment_name']
    course_name = request.session['course_name']

    try:
        assignment = Assignment.objects.get(name=assignment_name, course__name=request.session['course_name'])
    except Assignment.DoesNotExist:
        logging.warning('Assignment not found: ' + assignment_name)
        #This error message should be as it is, as the site can't load properly without this parameter
        return HttpResponse("No assignment found!")

    if assignment.parameter_injection:
        ParamaterFormSet = formset_factory(ColorForm, extra=0)
    attempts_left = None
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
        if not assignment.parameter_injection:
            form = EditorForm(request.POST)
        else:
            form = DoubleEditorForm(request.POST)

        if form.is_valid():
            if not assignment.parameter_injection:
                save_code(course_name, assignment_name, request.user.username, form.cleaned_data['text'])
            else:
                save_code(course_name, assignment_name, request.user.username, form.cleaned_data['parameters'] +
                          form.cleaned_data['text'])
            #docker run -v <volume: folder shared with docker container> --net='none' <no networking> -m <amount of memory to use> --rm='true'
            #-m not working on Ubuntu: p = subprocess.Popen(['docker', 'run', '--volume', '/root:/test', '--net', 'none', '--rm',
            # '-m', '50m', 'student_test', 'to_test.py', 'test']
            try:
                code_dir = Course.objects.get(name=course_name).student_code_dir + assignment_name.replace(" ","_") + \
                           '/' + request.user.username + '/'
                logging.info(code_dir)
                timeout = Assignment.objects.get(name=assignment_name, course__name=course_name).execution_timeout
                #Dockerfile has to be in the same directory where student code is or student code won't be found!
                subprocess.call(["cp", student_docker + "Dockerfile", code_dir])
            except Exception as e:
                logging.error( template.format(type(e).__name__, e.args))
                return redirect('error')
            try:
                build_out = open('/var/log/grader/docker_success_student', 'w')
                build_err = open('/var/log/grader/docker_error_student', 'w')

                #TODO: tää kans tappolistalle
                p = subprocess.Popen(['sudo', 'docker', 'build', '-t', 'student_image', code_dir],
                                     stdout=build_out, stderr=build_err)
                p.communicate()
            except:
                logging.error("Koodin ajoympäristöä ei voitu käynnistää. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan")
                if build_out not in locals()or build_err not in locals():
                    build_out.close()
                    build_err.close()
                return redirect('error')
            build_out.close()
            build_err.close()

            out_file = code_dir + "result.txt"
            err_file  = code_dir + "error.txt"
            #Run student code in Docker: Returns True if running succeeded and False if running took too long
            if run(code_dir, "student_image", out_file, err_file, timeout):
                #Should have something in either of these
                if not is_empty(out_file):
                    message = read_by_line(out_file)
                else:
                    if not is_empty(err_file):
                        error_message = read_by_line(err_file)
                    else:
                        logging.error("Both stdout and stderr files were empty")
                        return redirect('error')
            else:
                #TODO: Test this!
                error_message = "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."
        else:
            logging.error("Form validation error")
    #First time: No POST requests here
    else:
        if not assignment.parameter_injection:
            form = EditorForm()
        else:
            form = DoubleEditorForm()

        #Attempt to find student's code from previous visit
        #TODO: Test this!
        code_file = Course.objects.get(name=course_name).student_code_dir + '/' + assignment_name.replace(" ","_") +\
                    '/' + request.user.username + '/student_code.py'
        logging.debug("Old code loc " + code_file)
        if os.path.isfile(code_file):
            form.text = read_by_line(code_file)

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
@session_data
def grade(request):
    if request.method == 'POST':
        form = EditorForm(request.POST)
        message = ""
        error_message = ""
        assignment_name = request.session['assignment_name']
        course_name = request.session['course_name']

        try:
            assignment = Assignment.objects.get(name=assignment_name, course__name=request.session['course_name'])
        except Exception as e:
            logging.error(template.format(type(e).__name__, e.args))
            return redirect('error')

        attempts_left = 0	
        if assignment.attempts > 0:
            try:
                user_attempts = UserAttempts.objects.get(user__username=request.user.username,
                                                         assignment__id=assignment.id)
                #One attempt has been used
                attempts_left = user_attempts.attempts
                if attempts_left == 0:
                    return HttpResponse("Olet jo käyttänyt kaikki yrityskertasi")
            except UserAttempts.DoesNotExist:
                #User is trying this for the first time, create new db object that connects the user object to amount of
                #attempts the user has left to try this assignment
                to_add = UserAttempts()
                to_add.user = request.user
                to_add.assignment = assignment
                to_add.attempts = assignment.attempts
                attempts_left = assignment.attempts
                to_add.save()
            except Exception as e:
                logging.error(template.format(type(e).__name__, e.args))
                return redirect('error')

        if form.is_valid():
            #Save on valid form submission
            save_code(course_name, assignment_name, request.user.username, form.cleaned_data['text'])

            code_dir = Course.objects.get(name=course_name).student_code_dir + assignment_name.replace(" ","_") + '/'\
                       + request.user.username + '/'
            # Copy test files from assignment directory to the shared volume
            test_dir = Course.objects.get(name=request.session['course_name']).assignment_base_dir\
               + request.session['assignment_name'].replace(" ","_") + '/'
            logging.debug("Test_dir " + test_dir)
            #subprocess.call(["cp", test_dir + "/*", code_dir])
            subprocess.call(["cp", student_docker + "Dockerfile", code_dir])
            subprocess.call(["cp", example_docker + "Dockerfile", test_dir])
            description = imp.load_source('description', test_dir + 'description.py')

            results = []
            for test_name in description.tests:
                test = imp.load_source('test', test_dir + test_name)
                result = None
                if description.scale == "numeric":
                    result = NumericResult()
                elif description.scale == "pass":
                    result = BinaryResult()
                else:
                    logging.error("Faulty type of grading scale!")
                    return redirect('error')
                result.assignment = assignment
                result.test_name = test.name
                result.description = test.description
                result.user = request.user
                #result.save()

                test_result = None
                if test.type == "compare_output":
                    test_result = diff_test(test, code_dir, test_dir, result)
                    logging.debug(', '.join([' : '.join(
                        (k, str(test_result[k]))) for k in sorted(test_result, key=test_result. get, reverse=True)]))
                        result.feedback = test.test_results[0]

                #There was an error on test execution, student will not lose attempts
                if test_result['passed'] == "error":
                    logging.error(test_result['message'])
                    return redirect('error')
                elif test_result['passed'] == "yes":
                    logging.debug("Pass")
                    #If assignment.attempts > 0, then the number of attempts is limited
                    if assignment.attempts > 0:
                        user_attempts.attempts = attempts_left - 1
                        user_attempts.save()

                    if description.scale == "numeric":
                        result.type = "numeric"
                        result.score = test.points
                        result.max_score = test.points
                    elif description.scale == "pass":
                        result.type = "pass"
                        result.passed = True
                #Didn't pass!
                else:
                    logging.debug("Da No Pass")
                    #Assignment attempts were limited
                    if assignment.attempts > 0:
                        user_attempts.attempts = attempts_left - 1
                        user_attempts.save()

                    #Depending on the scale used, give some results
                    if description.scale == "numeric":
                        result.type = "numeric"
                        result.score = 0
                        result.max_score = test.points
                    elif description.scale == "pass":
                        result.type = "pass"
                        result.passed = False

                result.save()
                results.append(result)

        scored_points = 0
        for result in results:
            scored_points += result.score
            logging.debug("Code: " + result.student_result)

        success = False
        if scored_points >= description.points_required:
            success = True

        http = httplib2.Http()
        headers = {'Content-type': 'application/xml'}
        response, content = http.request(request.session['outcome_url'], 'POST', headers=headers)

        logging.debug("Response: " + response + " content: " + content)

        return render(request, "grade/results.html",
        {
            "assignment_name": assignment_name,
            "message": message,
            "error": error_message,
            "attempts_left": attempts_left,
            "results": results,
            "scored_points": scored_points,
            "total_points": description.total_points,
            "success": success,
        })
    #Not POST
    else:
        return HttpResponse("Eipäs kurkita!")

def error(request):
    return render(request, "grade/error.html", {})

def index(request):
    return HttpResponse("Tulit tänne suoraan kulkematta Canvas ruudun kautta")
