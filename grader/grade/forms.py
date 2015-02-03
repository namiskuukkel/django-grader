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
                raise forms.ValidationError("Yritit käyttää estettyä python käskyä")
        return value


class DoubleEditorForm(forms.Form):

    parameters = forms.CharField(widget=AceWidget(mode='python', theme='merbivore', width="575px", height="50px"),
                                   label="Laita tähän kenttään muuttujat omia testiajojasi varten",
				   required=False )
    text = forms.CharField(widget=AceWidget(mode='python', theme='merbivore'),label="")

    def clean_text(self):
        value = self.cleaned_data["text"]
        forbidden = ['exec(', 'eval(', 'exit(', 'quit(']
        for banned in forbidden:
            if banned in value:
                raise forms.ValidationError("Yritit käyttää estettyä python käskyä")

        if "parameters" in self.cleaned_data:
	    value2 = self.cleaned_data["parameters"]
            for banned in forbidden:
                if banned in value2:
                    raise forms.ValidationError("Yritit käyttää estettyä python käskyä")
        return value
