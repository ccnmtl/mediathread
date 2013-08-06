from django.test import TestCase
from mediathread.user_accounts.models import OrganizationModel
from mediathread.user_accounts import forms
from django.contrib.auth.models import User


class RegistrationFormTest(TestCase):
    """
    Test RegistrationForm
    """
    fixtures = ['unittest_sample_course.json']

    def setUp(self):
        self.valid_form_params = {
            'email': 'testmediathread@appsembler.com',
            'password': 'testpassword',
            'fullname': 'Appsembler Rocks',
            'position_title': 'PF',
            'hear_mediathread_from': 'OT',
            'subscribe_to_newsletter': True,
            'agree_to_term': True,
            'organization': 'TestCompany Inc.'
        }

        self.test_user = User.objects.get(username="test_student_one")
        self.test_organization = OrganizationModel.objects.create(name="Test Company")

    def test_valid_registration_form(self):
        test_valid_form = forms.RegistrationForm(self.valid_form_params)
        test_valid_form_model = test_valid_form.save(commit=False)
        self.assertEqual(test_valid_form.is_valid(), True)

        test_valid_form_model.organization = self.test_organization
        test_valid_form_model.user = self.test_user
        test_valid_form_model.save()
        test_valid_form.save()

    def test_invalid_registration_form(self):
        pass
