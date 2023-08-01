from courseaffils.models import Course
from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import RadioSelect
from registration.forms import RegistrationForm

from mediathread.main import course_details
from mediathread.main.course_details import (
    allow_public_compositions,
    all_items_are_visible, all_selections_are_visible,
    allow_item_download, allow_roster_changes)
from mediathread.projects.models import Project


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


class AcceptInvitationForm(forms.Form):

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.CharField(required=False)
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

    def clean(self):
        cleaned_data = super(AcceptInvitationForm, self).clean()

        username = cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).count() > 0:
                self._errors['username'] = self.error_class([
                    'This username already exists. Please choose another.'])

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            self._errors['password1'] = self.error_class(
                ['Passwords must match each other.'])
            self._errors['password2'] = self.error_class(
                ['Passwords must match each other.'])

        return cleaned_data


class CourseActivateForm(forms.Form):
    affil = forms.IntegerField(widget=forms.HiddenInput())
    course_name = forms.CharField(
        label='Course Title (required)',
        required=True)
    date_range_start = forms.DateField(
        label='',
        help_text='Start date',
        required=False)
    date_range_end = forms.DateField(
        label='',
        help_text='End date',
        required=False)
    request_consult_or_demo = forms.MultipleChoiceField(
        label='Would you like to request...',
        required=False,
        choices=(
            ('demo',
             'an in-class demonstration for your students led by a '
             'CTL learning designer'),
            ('setup_consult',
             'an instructor consultation about setup and use of Mediathread'),
            ('curricular_consult',
             'an instructor consultation on curricular and '
             'assessment design with Mediathread')),
        widget=forms.CheckboxSelectMultiple)
    how_will_mediathread_improve_your_class = forms.CharField(
        label='How do you envision Mediathread improving learning '
        'in your class? (Your answer will help us direct your inquiry '
        'to the appropriate CTL learning designer).',
        required=False,
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': ''}))
    hear_about_mediathread = forms.ChoiceField(
        label='How did you hear about Mediathread?',
        required=False,
        choices=(
            ('', '------'),
            ('demo', 'CTL Mediathread demo'),
            ('workshop', 'CTL Workshop'),
            ('recommendation_colleague', 'Recommendation from a colleague'),
            ('recommendation_student', 'Recommendation from a student'),
            ('other', 'Other')))
    used_mediathread = forms.ChoiceField(
        label='Have you used Mediathread before?',
        required=False,
        choices=(('yes', 'Yes'), ('no', 'No')),
        widget=forms.RadioSelect)


class DashboardSettingsForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title']

    class Media:
        js = ('js/lib/jquery.are-you-sure.js',
              'js/forms/unsaved-notice.js',)

    publish_to_world = forms.BooleanField(
        label='"Publish To The World" Compositions',
        required=False,
        help_text='This feature allows authors to publish compositions at a '
        'public level, via a link that does not require logging into '
        'Mediathread. Defaults to off.')
    see_eachothers_items = forms.BooleanField(
        label='Course members can see each other\'s items',
        required=False)
    see_eachothers_selections = forms.BooleanField(
        label='Course members can see each other\'s selections',
        required=False)
    allow_item_download = forms.BooleanField(
        label='Course instructors see a download item link',
        initial=False,
        required=False,
        help_text='Allow instructors to see a download link on the '
        'Item View page. This option is off by default.')
    allow_roster_changes = forms.BooleanField(
        label='Instructors can manage the course roster',
        initial=True,
        required=False,
        help_text='Allow instructors to manage course membership, by adding, '
        'removing, promoting and demoting students')
    reset = forms.BooleanField(
        widget=forms.HiddenInput,
        initial=False,
        required=False)

    @property
    def initial_data(self):
        return {
            'title': self.instance.title,
            'publish_to_world': False,
            'see_eachothers_items': True,
            'see_eachothers_selections': True,
            'allow_item_download': False,
            'allow_roster_changes': True
        }

    def __init__(self, *args, **kwargs):
        r = super(DashboardSettingsForm, self).__init__(*args, **kwargs)
        self.fields['publish_to_world'].initial = \
            allow_public_compositions(self.instance)
        self.fields['see_eachothers_items'].initial = \
            all_items_are_visible(self.instance)
        self.fields['see_eachothers_selections'].initial = \
            all_selections_are_visible(self.instance)
        self.fields['allow_item_download'].initial = \
            allow_item_download(self.instance)
        self.fields['allow_roster_changes'].initial = \
            allow_roster_changes(self.instance)
        return r

    def reset(self): # noqa F811
        return self.initial_data

    def clean(self):
        reset = self.data.get('reset')
        if reset is True or reset == 'True' or reset == 'true':
            return self.reset()

        cleaned_data = super(DashboardSettingsForm, self).clean()
        title = cleaned_data.get('title')
        if title is None or title.strip() == '':
            self.add_error('title', 'Title can\'t be blank.')

        return cleaned_data

    def save(self, *args, **kwargs):
        course = super(DashboardSettingsForm, self).save(*args, **kwargs)
        cleaned_data = self.cleaned_data

        course.add_detail(
            course_details.ITEM_VISIBILITY_KEY,
            int(cleaned_data.get('see_eachothers_items')))

        course.add_detail(
            course_details.SELECTION_VISIBILITY_KEY,
            int(cleaned_data.get('see_eachothers_selections')))

        course.add_detail(
            course_details.ALLOW_ITEM_DOWNLOAD_KEY,
            int(cleaned_data.get('allow_item_download')))

        course.add_detail(
            course_details.ALLOW_ROSTER_CHANGES_KEY,
            int(cleaned_data.get('allow_roster_changes')))

        if not cleaned_data.get('see_eachothers_selections'):
            Project.objects.limit_response_policy(course)

        course.add_detail(
            course_details.ALLOW_PUBLIC_COMPOSITIONS_KEY,
            int(cleaned_data.get('publish_to_world')))

        if not cleaned_data.get('publish_to_world'):
            Project.objects.reset_publish_to_world(course)

        return course
