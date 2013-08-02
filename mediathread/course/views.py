# Django
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group, User

# app
from .forms import *
from courseaffils.models import Course

# libs
from uuid import uuid4


class CourseCreateFormView(FormView):
    form_class = CourseForm
    template_name = 'course/create.html'
    success_url = '/'

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(CourseCreateFormView, self).get(*args, **kwargs)

    def form_valid(self, form):
        # preparing data
        course_title = form.cleaned_data['title']
        course_organization = form.cleaned_data['organization']

        ## the following code are for creating a course, should be refactored later into utils.py
        # create both student and facultu group for the course to be created
        student_group = Group.objects.create(name="student_%s" % uuid4())
        faculty_group = Group.objects.create(name="faculty_%s" % uuid4())
        student_group.save()
        faculty_group.save()

        # get user instance in session
        user = self.request.user  # TODO

        # faculties should join faculty group
        user.groups.add(faculty_group)
        created_course = Course.objects.create(
            group=student_group,
            faculty_group=faculty_group,
            title=course_title)
        created_course.save()

        return super(CourseCreateFormView, self).form_valid(form)


course_create = CourseCreateFormView.as_view()
