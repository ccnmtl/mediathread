# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lti_auth', '0002_auto_20151231_1107'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lticoursecontext',
            unique_together=set([('group', 'faculty_group')]),
        ),
    ]
