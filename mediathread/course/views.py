# Create your views here.

# Django
from django.views.generic.edit import FormView

# app
from .forms import *

class CourseCreateFormView(FormView):
    form_class = CourseForm
    template_name = 'course/create.html'
    success_url = '/'

    def form_valid(self, form):
        return super(CourseCreateFormView, eslf).form_valid(form)
        # TODO: create a courseaffils course

course_create = CourseCreateFormView.as_view()

