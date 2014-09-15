from django import forms
from captcha.fields import CaptchaField

TERM_CHOICES = (
    ('Fall', 'Fall'),
    ('Spring', 'Spring'),
    ('Summer', 'Summer'))


class RequestCourseForm(forms.Form):
    name = forms.CharField(required=True, max_length=512)
    email = forms.EmailField(required=True)
    uni = forms.CharField(required=True, max_length=512)

    course = forms.CharField(required=True, max_length=512)
    course_id = forms.CharField(required=True, max_length=512)

    term = forms.ChoiceField(required=True, choices=TERM_CHOICES)
    year = forms.CharField(required=True, max_length=512)

    instructor = forms.CharField(required=True, max_length=512)
    section_leader = forms.CharField(max_length=512, required=False)

    start = forms.DateField(required=True)
    end = forms.DateField(required=True)

    students = forms.IntegerField(required=True)
    assignments_required = forms.BooleanField(required=True)

    description = forms.CharField(widget=forms.Textarea, required=True)
    captcha = CaptchaField(required=True)

    title = forms.HiddenInput()
    pid = forms.HiddenInput()
    mid = forms.HiddenInput()
    type = forms.HiddenInput()
    owner = forms.HiddenInput()
    assigned_to = forms.HiddenInput()


class ContactUsForm(forms.Form):
    name = forms.CharField(required=True, max_length=512)
    email = forms.EmailField(required=True)
    username = forms.CharField(required=False, max_length=512)
    course = forms.CharField(required=True, max_length=512)

    issue_date = forms.DateTimeField(required=True)

    category = forms.CharField(required=True, max_length=512)

    description = forms.CharField(widget=forms.Textarea, required=True)
    captcha = CaptchaField(required=True)

    debug_info = forms.HiddenInput
    title = forms.HiddenInput()
    pid = forms.HiddenInput()
    mid = forms.HiddenInput()
    type = forms.HiddenInput()
    owner = forms.HiddenInput()
    assigned_to = forms.HiddenInput()

    def clean(self):
        cleaned_data = super(ContactUsForm, self).clean()

        if cleaned_data['category'] == '-----':
            self._errors["category"] = self.error_class([
                "An issue category is required"])

        return cleaned_data
