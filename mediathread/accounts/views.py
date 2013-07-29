from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation
from django.views.generic.edit import FormView
from django.shortcuts import render
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


class InviteStudents(FormView):
    form_class = InviteStudentsForm
    template_name = 'accounts/invite_students.html'

invite_students = InviteStudents.as_view()
