import uuid

from django.contrib.auth.models import Group
from django.db import models
from django.db.models.fields import UUIDField


class LTICourseContext(models.Model):
    group = models.ForeignKey(Group, related_name='course_group')
    faculty_group = models.ForeignKey(Group,
                                      related_name='course_faculty_group')
    uuid = UUIDField(default=uuid.uuid4, editable=False)
    enable = models.BooleanField(default=False)

    class Meta:
        unique_together = (('group', 'faculty_group'),)
