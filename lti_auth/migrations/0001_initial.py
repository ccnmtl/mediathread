# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='LTICourseContext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('lms_context_id', models.TextField()),
                ('faculty_group', models.ForeignKey(
                 related_name='course_faculty_group', to='auth.Group')),
                ('group', models.ForeignKey(related_name='course_group',
                                            to='auth.Group')),
            ],
        ),
    ]
