from django.views.generic.edit import FormView
from django.shortcuts import render
from .forms import RegistrationForm
from .forms import InviteStudentsForm


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'account/registration_form.html'

registration_form = RegistrationFormView.as_view()


class InviteStudents(FormView):
    form_class = InviteStudentsForm
    template_name = 'accounts/invite_students.html'

invite_students = InviteStudents.as_view()
