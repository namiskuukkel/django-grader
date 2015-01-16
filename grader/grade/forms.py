#!/usr/bin/python
# -*- coding: UTF-8 -*-

from django import forms
from django_ace import AceWidget

class EditorForm(forms.Form):
    text = forms.CharField(widget=AceWidget(mode='python', theme='GitHub'),label="")

    def clean_text(self):
        value = self.cleaned_data["text"]
        forbidden = ['exec(', 'eval(', 'exit(', 'quit(']
        for banned in forbidden:
            if banned in value:
                raise forms.ValidationError("Bannattu!")
        return value

class AvatarProfileForm(EditorForm):

    profile_avatar = forms.ImageField()

    class Meta(ProfileForm.Meta):
        fields = ProfileForm.Meta.fields + ['profile_avatar']