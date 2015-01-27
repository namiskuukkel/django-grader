#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django import forms
from django_ace import AceWidget

class EditorForm(forms.Form):
    text = forms.CharField(widget=AceWidget(mode='python', theme='monokai'),label="")

    def clean_text(self):
        value = self.cleaned_data["text"]
        forbidden = ['exec(', 'eval(', 'exit(', 'quit(']
        for banned in forbidden:
            if banned in value:
                raise forms.ValidationError("Bannattu!")
        return value


class DoubleEditorForm(EditorForm):

    parameters = forms.CharField(widget=AceWidget(mode='python', theme='monokai', width="575px", height="50px"),
                                   label="Laita tähän kenttään muuttujat omia testiajojasi varten")

    def clean_text(self):
        value = self.cleaned_data["text"]
        value2 = self.cleaned_data["parameters"]
        forbidden = ['exec(', 'eval(', 'exit(', 'quit(']
        for banned in forbidden:
            if banned in value or banned in value2:
                raise forms.ValidationError("Bannattu!")
        return value
