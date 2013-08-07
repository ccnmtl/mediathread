import autocomplete_light
from django import forms
from django.utils.safestring import mark_safe
from .models import RegistrationModel


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    agree_to_term = forms.BooleanField(required=True,
                                       label=mark_safe('I agree to the <a href="/terms-of-use">Terms of Service</a>'))
    organization = forms.CharField(widget=autocomplete_light.TextWidget('OrganizationAutocomplete'))
    password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField()
    last_name = forms.CharField()
    

    class Meta:
        model = RegistrationModel
        widget = autocomplete_light.get_widgets_dict(RegistrationModel)
        fields = [
            'position_title',
            'hear_mediathread_from',
            'subscribe_to_newsletter']


class InviteStudentsForm(forms.Form):
    email_from = forms.EmailField(label="From")
    student_emails = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}), label="To")
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
