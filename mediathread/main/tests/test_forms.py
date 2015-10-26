from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import UserFactory
from mediathread.main.forms import ContactUsForm, RequestCourseForm, \
    CourseDeleteMaterialsForm


class TestForms(TestCase):

    def test_request_course_form_fail(self):
        form = RequestCourseForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': 'foo'
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 1)
        self.assertTrue('decoy' in form._errors)

    def test_request_course_form_success(self):
        form = RequestCourseForm()
        form._errors = {}
        form.cleaned_data = {}

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_contact_us_form(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': 'foo',
            'category': '-----'
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 2)
        self.assertTrue('decoy' in form._errors)
        self.assertTrue('category' in form._errors)

    def test_course_manage_materials_form(self):
        user = UserFactory()
        request = RequestFactory().post('/')
        request.user = user

        form = CourseDeleteMaterialsForm(request=request)
        form._errors = {}
        form.cleaned_data = {
            'username': 'foo',
            'clear_all': True
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 1)
        self.assertTrue('username' in form._errors)

        form = CourseDeleteMaterialsForm(request=request)
        form._errors = {}
        form.cleaned_data = {
            'username': user.username,
            'clear_all': True
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)
