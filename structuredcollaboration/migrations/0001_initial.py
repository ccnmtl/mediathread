# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collaboration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=None, max_length=1024, null=True)),
                ('slug', models.SlugField(default=None, null=True, blank=True)),
                ('object_pk', models.CharField(max_length=255, null=True, verbose_name='object ID', blank=True)),
                ('_parent', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='children', default=None, blank=True, to='structuredcollaboration.Collaboration', null=True)),
            ],
            options={
                'ordering': ['title'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CollaborationPolicyRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('policy_name', models.CharField(max_length=512, choices=[(b'CourseProtected', b'Protected to Course Members'), (b'InstructorManaged', b'Instructors/Staff and user manage, Course members read'), (b'ProtectedEditorsAreOwners', b'Editors can manage the group,                                       Viewing requires authentication'), (b'InstructorShared', b'group/user manage/edit and instructors can view'), (b'CoursePublicCollaboration', b'Public Course Collaboration'), (b'CourseCollaboration', b'Course Collaboration'), (b'Assignment', b'Course assignment (instructors can manage/edit, course members can read/respond)'), (b'forbidden', b'Forbidden to everyone'), (b'PrivateStudentAndFaculty', b'Private between faculty and student'), (b'PublicParentEditorsAreOwners', b'Parent editors can manage the group,                                       Content is world-readable'), (b'PublicAssignment', b'Public Assignment (instructors can manage/edit, course members can respond, world can see)'), (b'ProtectedParentEditorsAreOwners', b'Parent editors can manage the group,                                       Viewing requires authentication'), (b'PublicEditorsAreOwners', b'Editors can manage the group,                                        Content is world-readable'), (b'PrivateEditorsAreOwners', b'User and group can view/edit/manage.                                       Staff can read')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='collaboration',
            name='_policy',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                default=None, blank=True, to='structuredcollaboration.CollaborationPolicyRecord', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='collaboration',
            name='content_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='collaboration_set_for_collaboration', blank=True, to='contenttypes.ContentType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='collaboration',
            name='context',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='context_children', default=None, blank=True, to='structuredcollaboration.Collaboration', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='collaboration',
            name='group',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                blank=True, to='auth.Group', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='collaboration',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='collaboration',
            unique_together=set([('content_type', 'object_pk')]),
        ),
    ]
