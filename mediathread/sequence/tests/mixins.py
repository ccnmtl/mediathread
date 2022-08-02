from mediathread.factories import UserFactory


class LoggedInTestMixin(object):
    def setUp(self):
        self.u = UserFactory(username='test_user')
        self.u.set_password('test')
        self.u.save()
        login = self.client.login(username='test_user',
                                  password='test')
        assert (login is True)
