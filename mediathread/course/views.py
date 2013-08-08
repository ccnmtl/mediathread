from uuid import uuid4

from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group

from mediathread.user_accounts.models import OrganizationModel, RegistrationModel
from courseaffils.models import Course
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

        # ensure the organization
        course_organization, org_created = OrganizationModel.objects.get_or_create(
            name=form.cleaned_data['organization'])

        ## the following code are for creating a course, should be refactored later into utils.py
        # create both student and facultu group for the course to be created
        student_group = Group.objects.create(name="student_%s" % uuid4())
        faculty_group = Group.objects.create(name="faculty_%s" % uuid4())

        # get user instance in session
        user = self.request.user  # TODO

        # faculties should join faculty group
        user.groups.add(faculty_group)
        user.groups.add(student_group)
        user.save()
        created_course = Course.objects.create(
            group=student_group,
            faculty_group=faculty_group,
            title=course_title)

        # create an information record for operations
        course_info = CourseInformation.objects.create(
            course=created_course,
            organization=course_organization,
            student_amount=course_student_amount)

        self.request.session['ccnmtl.courseaffils.course'] = created_course

        return super(CourseCreateFormView, self).form_valid(form)

    def get_initial(self):
        initial = self.initial.copy()
        try:
            initial['organization'] = self.request.user.registration_model.organization
        except RegistrationModel.DoesNotExist:
            pass
        return initial


course_create = CourseCreateFormView.as_view()
