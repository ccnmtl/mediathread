from django.views.generic.edit import FormView
from django.contrib.auth import authenticate, login
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation
from allauth.utils import get_user_model
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from .forms import InviteStudentsForm, RegistrationForm


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'user_accounts/registration_form.html'
    success_url = '/'

    def form_invalid(self, form):
        return super(RegistrationFormView, self).form_invalid(form)

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
        for email in emails:
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
                self.request.session['user_password'] = password
                send_email_confirmation(self.request, user, True)
        return super(InviteStudentsView, self).form_valid(form)

invite_students = InviteStudentsView.as_view()
