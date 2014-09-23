import factory
from django.contrib.auth.models import User, Group
from courseaffils.models import Course


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User


class GroupFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Group


class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Course
    title = "Sample Course"
    faculty_group = factory.SubFactory(GroupFactory)
    group = factory.SubFactory(GroupFactory)
