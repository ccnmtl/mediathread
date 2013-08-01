from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation
from allauth.utils import get_user_model
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from allauth.account.views import ConfirmEmailView as AllauthConfirmEmailView
from customerio import CustomerIO
from .forms import InviteStudentsForm, RegistrationForm


from pprint import pprint



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
    def post(self, *args, **kwargs):
        # perform login
        email_address = self.get_object().email_address

        user_to_login = User.objects.get(email=email_address.email)
        login_user(self.request, user_to_login)

        return super(ConfirmEmailView, self).post(*args, **kwargs)

confirm_email_view = ConfirmEmailView.as_view()


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'user_accounts/registration_form.html'
    success_url = '/'

    def form_valid(self, form):
        # another form for creating user in allauth
        signup_form = SignupForm({
            'username': '',
            'email': form.cleaned_data['email'],
            'password1': form.cleaned_data['password'],
            'password2': form.cleaned_data['password']
            })

        # save registration form for saving registration information
        if signup_form.is_valid():
            signup_user = signup_form.save(self.request)
            form.save()
        else:
            print "signup form is not valid"
            print signup_form.errors
            return super(RegistrationFormView, self).form_invalid(form)

        user_email = form.cleaned_data['email']
        user_model = get_user_model()
        user_obj = user_model.objects.get(email = user_email)

        login_username=user_obj.username
        login_password=form.cleaned_data['password']
        user_authentication_session = authenticate(username= login_username, password= login_password)
        #login(self.request, user_authentication_session)

        # TODO: add user to a specified course group

        return complete_signup(self.request, signup_user, app_settings.EMAIL_VERIFICATION, self.get_success_url())

registration_form = RegistrationFormView.as_view()


class InviteStudentsView(FormView):
    form_class = InviteStudentsForm
    template_name = 'user_accounts/invite_students.html'
    success_url = '/'

    def form_valid(self, form):
        course = self.request.session['ccnmtl.courseaffils.course']
        emails = form.cleaned_data['student_emails']
        cio = CustomerIO(settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)
        cio.identify(
            id=self.request.user.email,
            email=self.request.user.email,
            type="Teacher",
            first_name=self.request.user.first_name,
            last_name=self.request.user.last_name,
        )
        cio.track(
            customer_id=self.request.user.email,
            name="invited_student"
        )
        for email in emails:
            try:
                user = User.objects.get(email=email)
                course.group.user_set.add(user)
                cio.identify(
                    id=email,
                    email=email,
                    type="Student"
                )
                cio.track(
                    customer_id=user.email,
                    name='course_invite',
                    course_name=course.title,
                    invitor_name=self.request.user.get_full_name(),
                    invitor_email=form.cleaned_data['email_from'],
                    message=form.cleaned_data['message'],
                )
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
                    cio.identify(
                        id=email,
                        email=email,
                        type="Student"
                    )
                    send_email_confirmation(self.request, user, True)
        messages.success(self.request, "You've successfully invited {0} students.".format(
            len(emails)))
        return super(InviteStudentsView, self).form_valid(form)

invite_students = InviteStudentsView.as_view()
