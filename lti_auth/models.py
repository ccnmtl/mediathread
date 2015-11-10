from django.contrib.auth.models import Group
from django.db import models


class LTICourseContext(models.Model):
    group = models.ForeignKey(Group, related_name='course_group')
    faculty_group = models.ForeignKey(Group,
                                      related_name='course_faculty_group')
    lms_context_id = models.TextField()
