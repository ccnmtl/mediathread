from django import forms
from django.forms.widgets import RadioSelect
from registration.forms import RegistrationForm


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

    term = forms.ChoiceField(
        required=True, choices=TERM_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}))
    year = forms.CharField(required=True, max_length=512)

    instructor = forms.CharField(
        required=True, max_length=512,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    section_leader = forms.CharField(
        max_length=512, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    start = forms.DateField(required=True)
    end = forms.DateField(required=True)

    students = forms.IntegerField(required=True)
    assignments_required = forms.BooleanField(required=True)

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=True)

    decoy = forms.CharField(widget=forms.Textarea, required=False)

    title = forms.CharField(widget=forms.HiddenInput())
    pid = forms.CharField(widget=forms.HiddenInput())
    mid = forms.CharField(widget=forms.HiddenInput())
    type = forms.CharField(widget=forms.HiddenInput())
    owner = forms.CharField(widget=forms.HiddenInput())
    assigned_to = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(RequestCourseForm, self).clean()

        if 'decoy' in cleaned_data and len(cleaned_data['decoy']) > 0:
            self._errors["decoy"] = self.error_class([
                "Please leave this field blank"])

        return cleaned_data


class ContactUsForm(forms.Form):
    name = forms.CharField(required=True, max_length=512)
    email = forms.EmailField(required=True)
    username = forms.CharField(required=False, max_length=512)
    course = forms.CharField(required=True, max_length=512)

    issue_date = forms.DateTimeField(required=True)

    category = forms.CharField(required=True, max_length=512)

    description = forms.CharField(widget=forms.Textarea, required=True)

    decoy = forms.CharField(widget=forms.Textarea, required=False)

    debug_info = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(widget=forms.HiddenInput())
    pid = forms.CharField(widget=forms.HiddenInput())
    mid = forms.CharField(widget=forms.HiddenInput())
    type = forms.CharField(widget=forms.HiddenInput())
    owner = forms.CharField(widget=forms.HiddenInput())
    assigned_to = forms.CharField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(ContactUsForm, self).clean()

        if cleaned_data['category'] == '-----':
            self._errors["category"] = self.error_class([
                "An issue category is required"])

        if 'decoy' in cleaned_data and len(cleaned_data['decoy']) > 0:
            self._errors["decoy"] = self.error_class([
                "Please leave this field blank"])

        return cleaned_data


class CustomRegistrationForm(RegistrationForm):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    institution = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    referred_by = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control'}))
    user_story = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}))


class CourseDeleteMaterialsForm(forms.Form):
    username = forms.CharField(required=True)
    clear_all = forms.BooleanField(
        initial=False, required=False,
        widget=RadioSelect(choices=[(True, 'Yes'), (False, 'No')]))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CourseDeleteMaterialsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(CourseDeleteMaterialsForm, self).clean()

        if cleaned_data['username'] != self.request.user.username:
            self._errors['username'] = self.error_class([
                "Please enter your username"])

        return cleaned_data


class ActivateInvitationForm(forms.Form):
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class CourseActivateForm(forms.Form):
    course_name = forms.CharField(label='Course Name')
    consult_or_demo = forms.ChoiceField(
        label='Will you need a consultation or an in-class demo?',
        required=True,
        choices=(
            ('consultation', 'Consultation'),
            ('demo', 'In-class demo'),
            ('none', 'None')),
        widget=forms.RadioSelect,
        initial='none'
    )
