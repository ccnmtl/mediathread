from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mediathread.user_accounts.models import RegistrationModel
from .models import CourseInformation
from .forms import CourseForm


class CourseCreateFormView(FormView):
    """
    View that handles the creation of a new course by a logged in user.
    It stores the extra info in the CourseInformation model.
    """
    form_class = CourseForm
    template_name = 'course/create.html'
    success_url = '/'

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(CourseCreateFormView, self).get(*args, **kwargs)

    def form_valid(self, form):
        # preparing data
        course_title = form.cleaned_data['title']
        course_student_amount = form.cleaned_data['student_amount']
        course_organization_name = form.cleaned_data['organization']

        # creating course
        course = CourseInformation(
            title=course_title,
            organization_name=course_organization_name,
            student_amount=course_student_amount)
        course.save()

        # add user to that class as a faculty
        course.add_member(self.request.user, faculty=True)

        self.request.session['ccnmtl.courseaffils.course'] = course.course

        return super(CourseCreateFormView, self).form_valid(form)

    def get_initial(self):
        initial = self.initial.copy()
        try:
            initial['organization'] = self.request.user.registration_model.organization
        except RegistrationModel.DoesNotExist:
            pass
        return initial


course_create = CourseCreateFormView.as_view()
