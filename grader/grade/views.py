from .forms import SnippetForm
from .models import Snippet
from course_management.models import *
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def grade(request, course_name, assignment_name):

    if not 'course_id' in request.session or not 'outcome' in request.session:
        return HttpResponse("Missing parameters")

    assignment = Assignment.objects.get(name = assignment_name, course__id = request.session['course_id'])

    if assignment.count == 0:
        return HttpResponse("No assignment found!")
    elif assignment.count > 1:
        return HttpResponse("Too many assignments found!")

    attempts_left = 9999
    if assignment.attempts > 0:
        user_attempts = UserAttempts.objects.get(user__name=request.user.name)
        if user_attempts.count == 0:
            to_add = UserAttempts()
            to_add.user = request.user.id
            to_add.attempts = assignment.attempts
            attempts_left = assignment.attempts
            to_add.save()
        elif assignment.count > 1:
            return HttpResponse("Too many results found!")

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('/')
    else:
        form = SnippetForm()
        #TODO: user attempts!
    return render(request, "grade/editor.html", {
        "form": form,
        "snippets": Snippet.objects.all(),
        "user": request.user,
        "course": course_name,
        "assignment": assignment,
        "now": datetime.datetime.now(),
        "attempts_left": attempts_left,
    })
