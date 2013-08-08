from uuid import uuid4

from django.db import models
from django.contrib.auth.models import Group

from mediathread.user_accounts.models import OrganizationModel
from courseaffils.models import Course

STUDENT_AMOUNT_CHOICES = (
    (10, '1-9'),
    (20, '10-19'),
    (50, '20-49'),
    (100, '50-99'),
    (500, '100+')
)


class OrganizationIsEmptyException(Exception):
    """
    Organization could not be empty
    """
    pass


class GroupTypeIncorrectException(Exception):
    """
    Group type can be only member either or faculty
    """
    pass


class CourseInformation(models.Model):
    student_amount = models.IntegerField(choices=STUDENT_AMOUNT_CHOICES)
    organization = models.ForeignKey(OrganizationModel, null=True)
    course = models.ForeignKey('courseaffils.Course', null=True)
    sample_course = models.BooleanField(default=False)

    # uuid length is 36
    course_uuid = models.CharField(max_length=36, null=True)

    def __unicode__(self):
        if self.course:
            return self.course.title

    def __init__(self, title="Unknown Course", organization_name=None, **kwargs):
        if not organization_name:
            raise OrganizationIsEmptyException("must specify course_name in CourseInformation")

        super(CourseInformation, self).__init__(**kwargs)
        self.create_course(title, organization_name)

    def create_course(self, title, organization):
        """
            method to create a course instance in courseaffils
            title: string, the title of the course,
            organization: string, the name of the organization
        """
        # ensure the organization
        c_organization, org_created = OrganizationModel.objects.get_or_create(
            name=organization)

        # create both member and faculty groups with the same uuid
        course_uuid = self.course_uuid
        member_group = Group.objects.create(name="member_%s" % course_uuid)
        faculty_group = Group.objects.create(name="faculty_%s" % course_uuid)

        # create course instance in courseaffils
        course = Course.objects.create(
            group=member_group,
            faculty_group=faculty_group,
            title=title)
        course.save()

        # assigning data
        self.course = course
        self.organization, created = OrganizationModel.objects.get_or_create(
            name=organization)
        self.save()

    def get_group(self, type="member"):
        """
        Method for getting member or faculty group.
        type :: "member" | "faculty"
        """
        if type == "member":
            return self.course.group
        elif type == "faculty":
            return self.course.faculty_group
        else:
            raise GroupTypeIncorrectException("Group type is incorrect.")

    def add_member(self, user, faculty=False):
        """
        method for adding user into groups
        """
        member_group = self.get_group(type="member")
        faculty_group = self.get_group(type="faculty")

        user.groups.add(member_group)
        if faculty:
            # if faculty is True, add user to faculty group
            user.groups.add(faculty_group)

        user.save()

    def save(self):
        if not self.course_uuid:
            self.course_uuid = uuid4()
        return super(CourseInformation, self).save()
