from .forms import SnippetForm
from .models import Snippet
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def grade(request, course_name, assignment_name):

    if not 'course' in request.session or not 'assignment' in request.session or not 'outcome' in request.session:
        return HttpResponse("Missing parameters")

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('/')
    else:
        form = SnippetForm()
    return render(request, "grade/editor.html", {
        "form": form,
        "snippets": Snippet.objects.all(),
        "user": request.user
    })
