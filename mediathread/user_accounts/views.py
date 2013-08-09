import customerio
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.html import linebreaks
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from allauth.account.views import ConfirmEmailView as AllauthConfirmEmailView
from .forms import InviteStudentsForm, RegistrationForm


def login_user(request, user):
    """
        Log in a user without requiring credentials (using ``login`` from
        ``django.contrib.auth``, first finding a matching backend).
    """
    from django.contrib.auth import load_backend, login

    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        return login(request, user)


class ConfirmEmailView(AllauthConfirmEmailView):
    """
    View for comfirming user's email address and automatically login user
    """
    def post(self, *args, **kwargs):
        # perform login
        email_address = self.get_object().email_address
        user_to_login = User.objects.get(email=email_address.email)
        login_user(self.request, user_to_login)

        return super(ConfirmEmailView, self).post(*args, **kwargs)


confirm_email_view = ConfirmEmailView.as_view()


class RegistrationFormView(FormView):
    """
    View for registering new users to the application. Once the user enters
    the required data, he'll get an email with the activation link he needs to
    visit in order to activate his account.
    """
    form_class = RegistrationForm
    template_name = 'user_accounts/registration_form.html'
    success_url = '/'

    def form_valid(self, form):
        signup_params = {
            'email': form.cleaned_data['email'],
            'password': form.cleaned_data['password'],
            'organization': form.cleaned_data['organization'],
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name']
        }
        registration = form.instance
        success = registration.do_signup(self.request, **signup_params)
        if not success:
            signup_error = registration.get_form_errors()
            if signup_error.has_key('password1'):
                signup_error['password'] = signup_error['password1']
            form.errors.update(signup_error)
            return self.form_invalid(form)
        registration.save()

        # subscribe in mailchimp
        if registration.subscribe_to_newsletter:
            registration.subscribe_mailchimp_list(
                settings.MAILCHIMP_REGISTRATION_LIST_ID)

        return complete_signup(self.request, registration.get_user(),
                               app_settings.EMAIL_VERIFICATION,
                               self.get_success_url())


registration_form = RegistrationFormView.as_view()


class InviteStudentsView(FormView):
    """
    View that handles the inviting of students to a currently active class.
    Student will get an email notifying him that he is enrolled in a class,
    as well as an activation email if he doesn't already have an account
    in the system.
    """
    form_class = InviteStudentsForm
    template_name = 'user_accounts/invite_students.html'
    success_url = '/'

    def form_valid(self, form):
        course = self.request.session['ccnmtl.courseaffils.course']
        emails = form.cleaned_data['student_emails']
        cio = customerio.CustomerIO(settings.CUSTOMERIO_SITE_ID,
                                    settings.CUSTOMERIO_API_KEY)
        cio.identify(
            id=self.request.user.email,
            email=self.request.user.email,
            type="Instructor",
            first_name=self.request.user.first_name,
            last_name=self.request.user.last_name,
        )
        cio.track(
            customer_id=self.request.user.email,
            name="invited_student"
        )
        for email in emails:
            user = None
            cio.identify(
                id=email,
                email=email,
                type="Student"
            )
            try:
                user = User.objects.get(email=email)
                course.group.user_set.add(user)
            except User.DoesNotExist:
                password = "dummypass"
                signup_form = SignupForm({
                    'username': '',
                    'email': email,
                    'password1': password,
                    'password2': password,
                })
                if signup_form.is_valid():
                    user = signup_form.save(self.request)
                    course.group.user_set.add(user)
                    send_email_confirmation(self.request, user, True)
            if user:
                cio.track(
                    customer_id=user.email,
                    name='course_invite',
                    course_name=course.title,
                    invitor_name=self.request.user.get_full_name(),
                    invitor_email=form.cleaned_data['email_from'],
                    message=linebreaks(form.cleaned_data['message']),
                )
        return super(InviteStudentsView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(InviteStudentsView, self).get_context_data(**kwargs)
        context['course_name'] = self.request.session['ccnmtl.courseaffils.course']
        return context


invite_students = InviteStudentsView.as_view()
