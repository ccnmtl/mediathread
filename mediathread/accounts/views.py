from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation
from .forms import InviteStudentsForm, RegistrationForm

## DEBUG:
from pprint import pprint
## DEBUG

class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'accounts/registration_form.html'
    success_url = '/accounts/registration_done'

    def form_invalid(self, form):
        return super(RegistrationFormView, self).form_invalid(form)

    def form_valid(self, form):
        # TODO: create an account for it and send out a registration confirmation mail

        pprint(form)

        # another form for creating user in allauth
        signup_form = SignupForm({
            'username': '',
            'email': form.cleaned_data['email'],
            'password1': form.cleaned_data['password'],
            'password2': form.cleaned_data['password']
            })

        if signup_form.is_valid():
            signup_form.save(self.request)
            form.save()
        else:
            print "signup form is not valid"
            return super(RegistrationFormView, self).form_invalid(form)


        # save registration form for saving registration information

        return super(RegistrationFormView, self).form_valid(form)

registration_form = RegistrationFormView.as_view()


class InviteStudentsView(FormView):
    form_class = InviteStudentsForm
    template_name = 'accounts/invite_students.html'
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
