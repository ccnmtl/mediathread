from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from allauth.account.forms import SignupForm

from courseaffils.models import Course
from .utils import add_email_to_mailchimp_list


class RegistrationModel(models.Model):
    HEAR_CHOICES = (
        ('conference', 'Conference'),
        ('web_search', 'Web Search'),
        ('word_of_mouth', 'Word of mouth'),
        ('other', 'Other')
    )
    POSITION_CHOICES = (
        ('professor', 'Professor'),
        ('student', 'Student'),
        ('administrator', 'Administrator'),
        ('instructional_technologist', 'Instructional Technologist'),
        ('developer', 'Developer'),
        ('other', 'Other')
    )

    user = models.OneToOneField(User, editable=True, null=True, related_name="registration_model")
    organization = models.ForeignKey('OrganizationModel')
    hear_mediathread_from = models.CharField("How did you hear about Mediathread?",
                                             max_length=30, choices=HEAR_CHOICES)
    position_title = models.CharField("Which best describes you?", max_length=30, choices=POSITION_CHOICES)
    subscribe_to_newsletter = models.BooleanField("Yes, subscribe me to the Mediathread newsletter.")

    def do_signup(self, request, **kwargs):
        email = kwargs['email']
        password = kwargs['password']
        organization = kwargs['organization']
        first_name = kwargs['first_name']
        last_name = kwargs['last_name']

        signup_form = SignupForm({
            'username': '',
            'email': email,
            'password1': password,
            'password2': password,
        })

        if signup_form.is_valid():
            signup_user = signup_form.save(request)
            signup_user.first_name = first_name
            signup_user.last_name = last_name
            signup_user.save()

            sample_course = Course.objects.get(id=settings.SAMPLE_COURSE_ID)
            sample_course.user_set.add(signup_user)

            organization, created = OrganizationModel.objects.get_or_create(name=organization)
            self.organization = organization
            self.user = signup_user
            self.save()
        else:
            self.signupform_error_msg = signup_form.errors
            return False

        return signup_user

    def subscribe_mailchimp_list(self, list_id):
        add_email_to_mailchimp_list(self.user.email, list_id, fname=self.user.first_name, lname=self.user.last_name)

    def get_user(self):
        return self.user

    def get_form_errors(self):
        return self.signupform_error_msg


class OrganizationModel(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
