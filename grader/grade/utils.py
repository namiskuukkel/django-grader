#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging
from course_management.models import Course
from django.http import HttpResponse
from django.core.files import File
import subprocess, threading, os
from docker_settings import *
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
            #HARDCODED
            #Write student code to file
            with open(student_dir + "/student_code.py", 'w') as f:
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

'''def build_docker():
    try:
        logging.info("Building image")
        #Build docker image
        out = open('/home/docker/success', 'w')
        err = open('/home/docker/error', 'w')

        image = "test_environment"
        folder = "/home/docker/Student-Docker/"

        #Forcibly remove a previous image to avoid any old tests or student codes of messing things up
        subprocess.Popen(['sudo', 'docker', 'rmi', '-f', image])

        subprocess.Popen(['sudo', 'docker', 'build', '-t', image, folder],
                                     stdout=out, stderr=err)
        out.close()
        err.close()
        return "ok"
    except:
        return "Koodin ajoympäristöä ei voitu käynnistää. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan"'''

def build_docker(type, folder):

    logging.info("Building image")

    #This 'if' is for building a docker image based on different Dockerfiles
    #Student version will have 'python3.4 student_code_file' as ENTRYPOINT and Example has example code
    #This could be done with reading a varying code source to stdin in "docker run" subprocess, but this way
    #is significantly faster
    if type == "student":
        image = "student_image"
        #HARDCODED
    elif type == "example":
        image = "example_image"
        #HARDCODED
    else:
        return "Unknown docker type"

    try:
        #Forcibly remove a previous image to avoid any old tests or student codes of messing things up
        p = subprocess.Popen(['sudo', 'docker', 'rmi', '-f', image])
        #Wait for the previous image to be removed before continuing
        p.communicate()
        
	out = open('/var/log/grader/docker_success_' + type, 'w')
        err = open('/var/log/grader/docker_error_' + type, 'w')

	#TODO: tää kans tappolistalle
        subprocess.Popen(['sudo', 'docker', 'build', '-t', image, folder],
                                     stdout=out, stderr=err)
        return "ok"
    except:
        return "Koodin ajoympäristöä ei voitu käynnistää. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan"


def run(code_dir, image, out_file, err_file, timeout):
    p = None
    out = open(out_file, 'w')
    err = open(err_file, 'w')
    def target():
        #Volume: Share a folder with Docker container; 'folder_to_share':'folder_in_docker'
        #-w, working directory: Define working directory on Docker container
        #--net, networking: Networking settings for Docker container; none for no networking
        #--rm, remove: Automatically remove container after it finishes
        #image: The image which the container is built on
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
	out.close()
	err.close()
        return False
    out.close()
    err.close()
    return True

def is_empty(file):
    stream = open(file, 'r')
    stream.seek(0)
    #Check if the code run was succesful
    first_char = stream.read(1) #get the first character
    stream.close()
    if not first_char:
        return True
    else:
        return False

def read_by_line(file):
    message = ""
    output = open(file, 'r')
    for line in output:
        message += line + '\n'
        logging.debug("out:"+message)
    output.close()
    return message