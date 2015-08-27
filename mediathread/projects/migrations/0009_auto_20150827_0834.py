# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_auto_20150810_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_type',
            field=models.TextField(default=b'composition', db_index=True, choices=[(b'assignment', b'Composition Assignment'), (b'composition', b'Composition'), (b'selection-assignment', b'Selection Assignment')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='response_view_policy',
            field=models.TextField(default=b'always', choices=[(b'never', b'Never - Responses visible only to instructors'), (b'always', b'Always - Response not required to view other student responses'), (b'submitted', b'After Submission - Response required to view other student responses')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectversion',
            name='project_type',
            field=models.TextField(default=b'composition', db_index=True, choices=[(b'assignment', b'Composition Assignment'), (b'composition', b'Composition'), (b'selection-assignment', b'Selection Assignment')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectversion',
            name='response_view_policy',
            field=models.TextField(default=b'always', choices=[(b'never', b'Never - Responses visible only to instructors'), (b'always', b'Always - Response not required to view other student responses'), (b'submitted', b'After Submission - Response required to view other student responses')]),
            preserve_default=True,
        ),
    ]
