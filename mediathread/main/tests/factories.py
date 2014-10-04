import factory
from django.contrib.auth.models import User


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
