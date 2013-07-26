from django.views.generic.edit import FormView
from django.shortcuts import render
from .forms import RegistrationForm
from .forms import InviteStudentsForm


class RegistrationFormView(FormView):
    form_class = RegistrationForm
    template_name = 'accounts/registration_form.html'
    success_url = 'accounts/registration_done'

    def form_valid(self, form):
        # TODO: create an account for it and send out a registration confirmation mail
        return super(RegistrationFormView, self).form_valid(form)

registration_form = RegistrationFormView.as_view()


class InviteStudents(FormView):
    form_class = InviteStudentsForm
    template_name = 'accounts/invite_students.html'

invite_students = InviteStudents.as_view()
