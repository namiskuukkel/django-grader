from .models import Snippet
from django import forms
from django_ace import AceWidget


class EditorForm(forms.Form):
    text = forms.CharField(widget=AceWidget(mode='python', theme='monokai'))

    def clean_text(self):
        value = self.cleaned_data["text"]
        '''d" in value:
            raise forms.ValidationError("Must contain the string 'valid'")'''
        return value
