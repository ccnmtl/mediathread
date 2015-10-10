# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_assignmentitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='response_view_policy',
            field=models.TextField(default=b'always',
                                   choices=[(b'never', b'Never'),
                                            (b'submitted', b'On submission'),
                                            (b'always', b'Always')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectversion',
            name='response_view_policy',
            field=models.TextField(default=b'always',
                                   choices=[(b'never', b'Never'),
                                            (b'submitted', b'On submission'),
                                            (b'always', b'Always')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='project_type',
            field=models.TextField(
                default=b'composition',
                choices=[(b'assignment', b'Assignment'),
                         (b'composition', b'Composition'),
                         (b'selection-assignment', b'Selection Assignment')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectversion',
            name='project_type',
            field=models.TextField(
                default=b'composition',
                choices=[(b'assignment', b'Assignment'),
                         (b'composition', b'Composition'),
                         (b'selection-assignment', b'Selection Assignment')]),
            preserve_default=True,
        ),
    ]
