#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django import forms
from django_ace import AceWidget

class EditorForm(forms.Form):
    text = forms.CharField(widget=AceWidget(mode='python', theme='monokai'),label="Koodaa!")

    def clean_text(self):
        value = self.cleaned_data["text"]
        forbidden = ['exec(', 'eval(']
        for banned in forbidden:
            if banned in value:
                raise forms.ValidationError("Bannattu!")
        return value
