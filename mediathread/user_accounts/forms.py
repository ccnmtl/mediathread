from django import forms
from .models import RegistrationModel
import autocomplete_light

class RegistrationForm(forms.ModelForm):
    agree_to_term = forms.BooleanField(required=True)
    organization = forms.CharField(widget=autocomplete_light.TextWidget('OrganizationAutocomplete'))
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = RegistrationModel
        widget = autocomplete_light.get_widgets_dict(RegistrationModel)
        fields = [
                'email',
                'password',
                'fullname',
                'hear_mediathread_from',
                'position_title',
                'subscribe_to_newsletter']
        labels = {
                'email': 'Email',
                'fullname': 'Full',
                'password': 'Password',
                'hear_mediathread_from': 'Where did you hear Mediathread from?',
                'subscribe_to_newsletter': 'Subscribe our newsletter?',
                'agree_to_term': 'Agree to the Term of Service'
                }



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
