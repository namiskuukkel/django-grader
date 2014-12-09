#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
from course_management.models import Course
from django.http import HttpResponse
from django.core.files import File
import subprocess, threading, os

logging.basicConfig(filename='/var/log/grader/grader.log', level=logging.DEBUG)

def save_code(course_name, assignment_name, username, code):
    try:
        course = Course.objects.get(name=course_name)
        if course.use_gitlab is False:

            student_dir = course.student_code_dir + assignment_name.replace(" ", "_") + '/' + username
            #Note the character constraints on directory and file names!
            #student_dir = course.student_code_dir + '\\' + assignment_name + '\\' + username
            logging.info("attempt:" + student_dir)
            #Create student directory if one doesn't exist already
            if not os.path.exists(student_dir):
                try:
                    os.makedirs(student_dir)
                except Exception as e:
                    template = "An exception of type {0} occured. Arguments:\n{1!r}"
                    message = template.format(type(e).__name__, e.args)
                    return message
            #Write student code to file
            with open(student_dir + "/to_test.py", 'w') as f:
                file = File(f)
                file.write(code)

            return "ok"
        else:
            # TODO
            #Myös TODO: Jos github tallennus failaa, tee lokaali kopio
            print("stuff")
    except Course.DoesNotExist:
        logging.warning('Course not found: ' + course_name)
        return "No course found!"
    except:
        return "Koodin tallennus epäonnistui. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan"

def build_docker():
    try:
        logging.info("Building image")
        #Build docker image
        out = open('/home/docker/success', 'w')
        err = open('/home/docker/error', 'w')

        image = "test_environment"
        folder = "/home/docker/Run-Docker/"

        #Forcibly remove a previous image to avoid any old tests or student codes of messing things up
        subprocess.Popen(['sudo', 'docker', 'rmi', '-f', image])

        subprocess.Popen(['sudo', 'docker', 'build', '-t', image, folder],
                                     stdout=out, stderr=err)
        out.close()
        err.close()
        return "ok"
    except:
        return "Koodin ajoympäristöä ei voitu käynnistää. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan"

'''def build_docker(type):
    try:
        logging.info("Building image")
        #Build docker image
        out = open('/home/docker/success', 'w')
        err = open('/home/docker/error', 'w')
        if type == "run":
            image = "student_run"
            folder = "/home/docker/Run-Docker/"
        elif type == "grade":
            image = "student_grade"
            folder = "/home/docker/Grade-Docker/"
        else:
            return

        #Forcibly remove a previous image to avoid any old tests or student codes of messing things up
        subprocess.Popen(['sudo', 'docker', 'rmi', '-f', image])
        subprocess.Popen(['sudo', 'docker', 'build', '-t', image, folder],
                                     stdout=out, stderr=err)
        out.close()
        err.close()
    except:
        return HttpResponse("Koodin ajoympäristöä ei voitu käynnistää. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan")
'''

def run(code_dir, image, out, err, timeout):
    p = None
    def target():
        p = subprocess.Popen(['sudo', 'docker', 'run', '--volume', code_dir + ':/test' ,'-w', '/test',
                              '--net', 'none', '--rm', image], stdout=out, stderr=err)
        #Wait for process to terminate
        p.communicate()

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        p.terminate()
        thread.join()
        return False
    return True

def is_empty(stream):
    stream.seek(0)
    #Check if the code run was succesful
    first_char = stream.read(1) #get the first character
    if not first_char:
        return True
    else:
        return False