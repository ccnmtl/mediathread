from django.test.client import RequestFactory
from django.test.testcases import TestCase

from mediathread.factories import UserFactory
from mediathread.main.forms import ContactUsForm, \
    CourseDeleteMaterialsForm, AcceptInvitationForm


class TestForms(TestCase):

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

    def test_accept_invitation_form(self):
        form = AcceptInvitationForm()

        form._errors = {}

        form.cleaned_data = {
            'first_name': 'Foo', 'last_name': 'Bar', 'password1': 'test',
            'password2': 'test', 'username': 'testname'
        }
        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_accept_invitation_form_duplicate_username(self):
        user = UserFactory()
        form = AcceptInvitationForm()

        # required fields
        form._errors = {}
        form.cleaned_data = {
            'first_name': 'Foo', 'last_name': 'Bar', 'password1': 'test',
            'password2': 'test', 'username': user.username
        }
        form.clean()
        self.assertEquals(len(form._errors.keys()), 1)
        self.assertTrue('username' in form._errors)

    def test_accept_invitation_form_invalid_passwords(self):
        form = AcceptInvitationForm()

        # required fields
        form._errors = {}
        form.cleaned_data = {
            'first_name': 'Foo',
            'last_name': 'Bar',
            'password1': 'a',
            'password2': 'b',
            'username': 'testname'
        }
        form.clean()
        self.assertEquals(len(form._errors.keys()), 2)
        self.assertTrue('password1' in form._errors)
        self.assertTrue('password2' in form._errors)
