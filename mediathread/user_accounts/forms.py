from django import forms
from .models import RegistrationModel

class RegistrationForm(forms.ModelForm):
    agree_to_term = forms.BooleanField(required=True)

    class Meta:
        model = RegistrationModel


class InviteStudentsForm(forms.Form):
    email_from = forms.EmailField()
    student_emails = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))

    def clean_student_emails(self):
        data = self.cleaned_data['student_emails'].splitlines()
        emails = []
        for email in data:
            if "@" in email:
                emails.append(email.strip())
            else:
                raise forms.ValidationError("Error in an email address")
        return emails
