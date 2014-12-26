#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import logging
from .utils import *
from .models import TestResult
logging.basicConfig(filename='/var/log/grader/grader.log', level=logging.DEBUG)

def diff_test(test, code_dir, test_dir, result):
    #STUDENT PART
    try:
        build_docker("student")
    except:
        return {"pass": "error",
                "message": "Error building student docker." }
    try:
        out = open(code_dir + test + '_student_result.txt', 'w')
        err = open(code_dir + test + '_student_error.txt', 'w')
    except:
        return {"pass": "error",
                "message": "Failed to open result files for writing" }
    try:
        if run(code_dir, "student_image", out, err, test["timeout"]):
            #Close and open again for reading (some errors appeared with w+)
            out.close()
            err.close()
            out = open(code_dir + 'result.txt', 'r')
            err = open(code_dir + 'error.txt', 'r')

            #Should have something in either of these
            if not is_empty(out):
                result.student_result = out.read()
                result.save()
            else:
                if not is_empty(err):
                    result.student_result = err.read()
                    result.feedback = "Koodisi tuotti virheen."
                    #result.save()
                    return {"pass": "no",
                            "message": "error"}
                else:
                    return {"pass": "error",
                            "message": "Docker wrote no results!" }
        else:
            result.student_result = "Keskeytetty"
            result.feedback = "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."
            #result.save()
            return {"pass": "no",
                    "message": "timeout"}
        out.close()
        err.close()
    except:
        return {"pass": "error",
                "message": "Error running docker" }

    #Remove the old files so you can be sure that there are no left overs on the next run
    try:
        os.remove(code_dir + test + '_student_result.txt')
        os.remove(code_dir + test + '_student_error.txt')
    except:
        return {"pass": "error",
                "message": "Failed to remove result files" }

    #EXAMPLE PART
    needs_running = True
    try:
        example_age = os.path.getmtime(test_dir + "example.py")
    except:
        return {"pass": "error",
                "message": "Example.py not found" }

    try:
        example_result_age = os.path.getmtime(test_dir + test + "_expected_output")
        #If example.py is a newer file than expected output file for this test, the test needs to be run with the new
        #example.py file
        if example_age < example_result_age:
            needs_running = False
    except:
        pass
    if not needs_running:
        expected = open(code_dir + test + "_expected_output.txt", "r")
    else:
        try:
            build_docker("example")
        except:
            return {"pass": "error",
                    "message": "Error building example docker." }
        try:
            expected = open(code_dir + test + '_expected_output.txt', 'w')
            example_err = open(code_dir + test + '_student_error.txt', 'w')
        except:
            return {"pass": "error",
                    "message": "Failed to open example result files for writing" }
        try:
            if run(test_dir, "example_image", expected, example_err, test["timeout"]):
                #Close and open again for reading (some errors appeared with w+)
                out.close()
                err.close()
                try:
                    expected = open(test_dir + 'result.txt', 'r')
                    example_err = open(test_dir + 'error.txt', 'r')
                except:
                    return {"pass": "error",
                    "message": "Failed to open result files for reading" }
                #Should have something in either of these
                if is_empty(expected):
                    if is_empty(example_err):
                        return {"pass": "error",
                                "message": "Docker wrote no results!" }
                    else:
                        return {"pass": "error",
                                "message": "Example code produced an error" }
            else:
                return {"pass": "error",
                        "message": "Example code running ran out of time"}
        except:
            return {"pass": "error",
            "message": "Error running example docker" }

    logging.DEBUG(expected.read() + 'vs' + result.student_result)
    if expected.read() != result.student_result:
        return {"pass": "no",
                "message": "unequal"}
