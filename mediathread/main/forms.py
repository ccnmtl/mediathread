from django import forms
from captcha.fields import CaptchaField


class RequestCourseForm(forms.Form):
    name = forms.CharField(required=True, max_length="512")
    email = forms.EmailField(required=True)
    uni = forms.CharField(required=True, max_length=512)

    course = forms.CharField(required=True, max_length="512")
    course_id = forms.CharField(required=True, max_length="512")

    term = forms.CharField(required=True, max_length="512")
    year = forms.CharField(required=True, max_length="512")

    instructor = forms.CharField(required=True, max_length="512")
    section_leader = forms.CharField(max_length="512")

    start = forms.DateField()
    end = forms.DateField()

    students = forms.IntegerField()
    assignments_required = forms.BooleanField()

    description = forms.CharField(widget=forms.Textarea)
    captcha = CaptchaField()
