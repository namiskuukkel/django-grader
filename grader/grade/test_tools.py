#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django.http import HttpResponse
import os
import utils

def diff_test(test, code_dir, result):

    try:
        utils.build_docker("student")
    except:
        return {"pass": "error",
                "message": "Tapahtui virhe! Koodin ajaminen epäonnistui. "
                           "Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan" }
    try:
        message = ""
        successful = True
        out = open(code_dir + test + '_student_result.txt', 'w')
        err = open(code_dir + test + '_student_error.txt', 'w')

        if utils.run(code_dir, "student_image", out, err, test["timeout"]):
            #Close and open again for reading (some errors appeared with w+)
            out.close()
            err.close()
            out = open(code_dir + 'result.txt', 'r')
            err = open(code_dir + 'error.txt', 'r')
            #Should have something in either of these
            if not utils.is_empty(out):
                result.write("Ohjelmasi tulosti:")
                result.write(out.read())
            else:
                if not utils.is_empty(err):
                    result.write("Ohjelmasi tuotti virheen:")
                    result.write(err.read())
                    successful = False
                else:
                    return {"pass": "error",
                            "message": "Oops! You shouldn't have gotten here!" }
        else:
            return {"pass": "no",
                    "message": "Koodin ajamisessa kesti liian kauan. Ajo keskeytettiin."}

        out.close()
        err.close()
        return "ok"
    except:
        return {"pass": "error",
                "message": "Tapahtui virhe! Koodin ajaminen epäonnistui. "
                           "Jos virhe toistuu, ota yhteyttä kurssihenkilökuntaan" }
            #Remove the old files so you can be sure that there are no left overs on the next run
        os.remove(code_dir + test + '_result.txt')
        os.remove(code_dir + test + '_error.txt')