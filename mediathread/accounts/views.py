from django.views.generic.edit import FormView
from .forms import InviteStudentsForm


class InviteStudents(FormView):
    form_class = InviteStudentsForm
    template_name = 'accounts/invite_students.html'

invite_students = InviteStudents.as_view()
