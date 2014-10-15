#!/usr/bin/python
# -*- coding: UTF-8 -*-

from .forms import EditorForm
from course_management.models import *
import course_management.course_settings as course_settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.core.files import File
import subprocess, threading, os
import logging

logging.basicConfig(filename='Logs/grader.log', level=logging.DEBUG)

@login_required
def code(request):
    message = ""
    if not 'course_id' in request.session or not 'outcome' in request.session or not 'course_name' in request.session\
            or not 'assignment_name' in request.session:
        return HttpResponse("Missing parameters")

    #Fetch the object matching the assignment name given by the LTI
    #TODO: match coursename also!
    #TODO: make assignment unique
    assignment_name = request.session['assignment_name']
    course_name = request.session['course_name']

    try:
        assignment = Assignment.objects.get(name = assignment_name, course__id = request.session['course_id'] )
    except Assignment.DoesNotExist:
        logging.warning('Assignment not found: ' + assignment_name)
        return HttpResponse("No assignment found!")

    attempts_left = 9999
    #If assignment.attempts > 0, then the number of attempts is limited
    if assignment.attempts > 0:
        try:
            #TODO: match the assignment as well
            user_attempts = UserAttempts.objects.get(user__name=request.user.username,
                                                     assignment__name = assignment.name)
        except UserAttempts.DoesNotExist:
            #User is trying this for the first time, create new db object that connects the user object to amount of
            #attempts the user has left to try this assignment
            to_add = UserAttempts()
            to_add.user = request.user.id
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

            try:
                #Build container
                p = subprocess.Popen(['docker', 'build', '-t', 'student_run', 'Run-Docker'])
            except:
                message="Koodin ajoympäristöä ei voitu käynnistää. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan"
                pass
            try:
                out = open('result.txt', 'wr')
                err = open('error.txt', 'wr')
                def target():
                    p = subprocess.Popen(['docker', 'run', '--volume', course_settings.student_code_dir + '/'
                                          + assignment_name + '/' + request.user.username +':/test',
                                          '--net', 'none', '--rm', 'student_run'], stdout=out, stderr=err)
                    #Wait for process to terminate
                    p.communicate()

                thread = threading.Thread(target=target)
                thread.start()
                #TODO: Hae asetuksista
                thread.join(15)
                if thread.is_alive():
                    print 'Terminating process'
                    p.terminate()
                    thread.join()
                    message = "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."
                else:
                    message = out.read() + '&' + err.read()
                out.close()
                err.close()

            except:
                message = "Tapahtui virhe! Koodin ajaminen epäonnistui." \
                          "Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan"
                pass

            return redirect('/')
    else:
        form = EditorForm()
        code_file = course_settings.student_code_dir + '/' + assignment_name + '/' + request.user.username+'/to_test.py'
        if os.path.isfile(code_file ):
            f = open(code_file, 'r')
            form.text = f.read()

    #TODO: user attempts!
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
    code_dir = course_settings.student_code_dir + '/' + request.session['assignment_name'] + '/' + request.user.username
    subprocess.call(["cp", course_settings.assignment_base_dir + "/"
                     + request.session['assignment_name'] + "/*", code_dir])
    p = subprocess.Popen(['docker', 'run', '--volume', code_dir +':/test', '--net', 'none', '--rm', 'student_test'])

def save(course_name, assignment_name, username, code):
    try:
        if course_settings.use_gitlab is False:
            student_dir = course_settings.student_code_dir + '/' + assignment_name + '/' + username
            if not os.path.exists(student_dir):
                os.makedirs(student_dir)
            f = open(student_dir + "/to_test.py", 'w')
            file = File(f)
            file.write(code)
            f.close()
        else:
            #TODO
            #Myös TODO: Jos github tallennus failaa, tee lokaali kopio
            print("stuff")
    except:
        return HttpResponse("")