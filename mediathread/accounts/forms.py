from django import forms
from .models import RegistrationModel

class RegistrationForm(forms.ModelForm):

    agree_to_term = forms.BooleanField(required=True)

    class Meta:
        model = RegistrationModel


class InviteStudentsForm(forms.Form):
    student_emails = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
