# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('structuredcollaboration', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='collaboration',
            old_name='_policy',
            new_name='policy_record',
        ),
        migrations.AlterField(
            model_name='collaborationpolicyrecord',
            name='policy_name',
            field=models.CharField(max_length=512,
                                   choices=[(b'CourseProtected',
                                             b'Protected to Course Members'),
                                            (b'InstructorManaged', b'Instructors/Staff and user manage, Course members read'), (b'CoursePublicCollaboration', b'Public Course Collaboration'), (b'CourseCollaboration', b'Course Collaboration'), (b'Assignment', b'Course assignment (instructors can manage/edit, course members can read/respond)'), (b'forbidden', b'Forbidden to everyone'), (b'PrivateStudentAndFaculty', b'Private between faculty and student'), (b'PublicAssignment', b'Public Assignment (instructors can manage/edit, course members can respond, world can see)'), (b'PrivateEditorsAreOwners', b'User and group can view/edit/manage.                                       Staff can read'), (b'PublicEditorsAreOwners', b'Editors can manage the group,                                        Content is world-readable'), (b'InstructorShared', b'group/user manage/edit and instructors can view')]),
            preserve_default=True,
        ),
    ]
