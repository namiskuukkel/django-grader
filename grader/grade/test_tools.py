#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import logging
from .utils import *

logging.basicConfig(filename='/var/log/grader/grader.log', level=logging.DEBUG)


def diff_test(test, code_dir, test_dir, result):
    ################### STUDENT PART ##########################
    success = build_docker('student_image', code_dir)
    if success != "ok":
        logging.error("Koodin ajoympäristöä ei voitu käynnistää. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan")
        return {"pass": "error",
                "message": "Error building student docker."}

    out_file = code_dir + test.name.replace(" ", "_") + '_student_result.txt'
    err_file = code_dir + test.name.replace(" ", "_") + '_student_error.txt'

    #We do not want any old stuff to exist at this point, e.g. error file not empty because of previous run
    if os.path.isfile(out_file):
        os.remove(out_file)
    if os.path.isfile(out_file):
        os.remove(err_file)
    logging.debug('Code_dir: ' + code_dir+'/student_code.py')
    try:
        if run(code_dir+'/student_code.py', "student_image", out_file, err_file, test.timeout):
            #Should have something in either of these
            if not is_empty(out_file):
                result.student_result = read_by_line(out_file)
                #result.save()
            else:
                if not is_empty(err_file):
                    result.student_result = read_by_line(err_file)
                    result.feedback = "Koodisi tuotti virheen."
                    #result.save()
                    return {"passed": "no",
                            "message": "error"}
                else:
                    return {"passed": "error",
                            "message": "Docker wrote no results!"}
        else:
            result.student_result = "Keskeytetty"
            result.feedback = "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."
            #result.save()
            return {"passed": "no",
                    "message": "timeout"}
    except Exception as e:
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        logging.error(template.format(type(e).__name__, e.args))
        return {"passed": "error",
                "message": "Error running docker"}

    ###########################EXAMPLE PART##########################
    needs_running = True
    try:
        example_age = os.path.getmtime(test_dir + "/example.py")
    except:
        return {"passed": "error",
                "message": "Example.py not found"}

    expected_file = test_dir + test.name.replace(" ", "_") + "_expected_output"
    try:
        example_result_age = os.path.getmtime(expected_file)
        #If example.py is a newer file than expected output file for this test, the test needs to be run with the new
        #example.py file
        if example_age < example_result_age:
            needs_running = False
    except:
        #Expected output file didn't exist
        pass

    if needs_running:
        success = build_docker('example_image', test_dir)
        if success != "ok":
            return {"passed": "error",
                    "message": "Error building example docker."}

        error_file = test_dir + test.name.replace(" ", "_") + '_unexpected_error'

        try:
            logging.debug("Test_dir " + test_dir)
            if run(test_dir+'/example.py', "example_image", expected_file, error_file, test.timeout):
                #Should have something in either of these
                if is_empty(expected_file):
                    logging.debug("expected empty")
                    if is_empty(error_file):
                        return {"passed": "error",
                                "message": "Docker wrote no results!"}
                    else:
                        logging.error("Example produced: " + read_by_line(error_file))
                        return {"passed": "error",
                                "message": "Example code produced an error"}
            else:
                return {"passed": "error",
                        "message": "Example code running ran out of time"}
        except:
            return {"passed": "error",
                    "message": "Error running example docker"}

    expected = read_by_line(expected_file)
    logging.debug(expected + ' vs ' + result.student_result)
    if expected != result.student_result:
        return {"passed": "no",
                "message": "unequal"}
    else:
        return {"passed": "yes",
                "message": ""}


def inject_diff_test(test, code_dir, test_dir, result):
    ################### STUDENT PART ##########################
    success = build_docker('student_image', code_dir)
    if success != "ok":
        logging.error("Koodin ajoympäristöä ei voitu käynnistää. Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan")
        return {"pass": "error",
                "message": "Error building student docker."}

    out_file = code_dir + test.name.replace(" ", "_") + '_student_result.txt'
    err_file = code_dir + test.name.replace(" ", "_") + '_student_error.txt'

    #We do not want any old stuff to exist at this point, e.g. error file not empty because of previous run
    if os.path.isfile(out_file):
        os.remove(out_file)
    if os.path.isfile(out_file):
        os.remove(err_file)

    modified_code_student = code_dir + test.name.replace(" ", "_") + 'modified_student_code.py'
    #Add some preset parameters in the beginning of the file that is run in docker
    modified = open(modified_code_student, 'w')
    for parameter in test.parameters:
        modified.write(parameter + '\n')
    code = read_by_line(code_dir+'/student_code.py')
    modified += code
    modified.close()

    try:
        if run(modified_code_student, "student_image", out_file, err_file, test.timeout):
            #Should have something in either of these
            if not is_empty(out_file):
                result.student_result = read_by_line(out_file)
                #result.save()
            else:
                if not is_empty(err_file):
                    result.student_result = read_by_line(err_file)
                    result.feedback = "Koodisi tuotti virheen."
                    #result.save()
                    return {"passed": "no",
                            "message": "error"}
                else:
                    return {"passed": "error",
                            "message": "Docker wrote no results!"}
        else:
            result.student_result = "Keskeytetty"
            result.feedback = "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."
            #result.save()
            return {"passed": "no",
                    "message": "timeout"}
    except Exception as e:
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        logging.error(template.format(type(e).__name__, e.args))
        return {"passed": "error",
                "message": "Error running docker"}

    ###########################EXAMPLE PART##########################
    needs_running = True
    try:
        example_age = os.path.getmtime(test_dir + "/example.py")
    except:
        return {"passed": "error",
                "message": "Example.py not found"}

    expected_file = test_dir + test.name.replace(" ", "_") + "_expected_output"
    try:
        example_result_age = os.path.getmtime(expected_file)
        #If example.py is a newer file than expected output file for this test, the test needs to be run with the new
        #example.py file
        if example_age < example_result_age:
            needs_running = False
    except:
        #Expected output file didn't exist
        pass

    if needs_running:
        success = build_docker('example_image', test_dir)
        if success != "ok":
            return {"passed": "error",
                    "message": "Error building example docker."}

        error_file = test_dir + test.name.replace(" ", "_") + '_unexpected_error'

        modified_code_example = test_dir + test.name.replace(" ", "_") + 'modified_example_code.py'
        #Add some preset parameters in the beginning of the file that is run in docker
        modified = open(modified_code_example, 'w')
        for parameter in test.parameters:
            modified.write(parameter + '\n')
        code = read_by_line(test_dir + "/example.py")
        modified += code
        modified.close()

        try:
            logging.debug("Test_dir " + test_dir)
            if run(modified_code_example, "example_image", expected_file, error_file, test.timeout):
                #Should have something in either of these
                if is_empty(expected_file):
                    logging.debug("expected empty")
                    if is_empty(error_file):
                        return {"passed": "error",
                                "message": "Docker wrote no results!"}
                    else:
                        logging.error("Example produced: " + read_by_line(error_file))
                        return {"passed": "error",
                                "message": "Example code produced an error"}
            else:
                return {"passed": "error",
                        "message": "Example code running ran out of time"}
        except:
            return {"passed": "error",
                    "message": "Error running example docker"}

    expected = read_by_line(expected_file)
    logging.debug(expected + ' vs ' + result.student_result)
    if expected != result.student_result:
        return {"passed": "no",
                "message": "unequal"}
    else:
        return {"passed": "yes",
                "message": ""}
