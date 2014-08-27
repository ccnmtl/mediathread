from django import forms
from captcha.fields import CaptchaField

TERM_CHOICES = (
    ('Fall', 'Fall'),
    ('Spring', 'Spring'),
    ('Summer', 'Summer'))


class RequestCourseForm(forms.Form):
    name = forms.CharField(required=True, max_length="512")
    email = forms.EmailField(required=True)
    uni = forms.CharField(required=True, max_length=512)

    course = forms.CharField(required=True, max_length="512")
    course_id = forms.CharField(required=True, max_length="512")

    term = forms.ChoiceField(required=True, choices=TERM_CHOICES)
    year = forms.CharField(required=True, max_length="512")

    instructor = forms.CharField(required=True, max_length="512")
    section_leader = forms.CharField(max_length="512")

    start = forms.DateField(required=True)
    end = forms.DateField(required=True)

    students = forms.IntegerField(required=True)
    assignments_required = forms.BooleanField(required=True)

    description = forms.CharField(widget=forms.Textarea, required=True)
    captcha = CaptchaField(required=True)
