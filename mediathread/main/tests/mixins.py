from django.contrib.auth.models import User
from mediathread.factories import UserFactory


class LoggedInUserTestMixin(object):
    def setUp(self):
        self.u = UserFactory(username='test_user')
        self.u.set_password('test')
        self.u.save()
        login = self.client.login(username='test_user', password='test')
        assert (login is True)


class LoggedInSuperuserTestMixin(object):
    def setUp(self):
        self.u = User.objects.create_superuser(
            username='test_admin',
            email='abc@example.com',
            password='test')
        login = self.client.login(username='test_admin', password='test')
        assert (login is True)
