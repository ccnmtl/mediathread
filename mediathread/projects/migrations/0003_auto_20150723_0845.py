# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20150722_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.TextField(default=b'composition',
                                   choices=[(b'Assignment', b'assignment'),
                                            (b'Composition', b'composition')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectversion',
            name='project_type',
            field=models.TextField(default=b'composition',
                                   choices=[(b'Assignment', b'assignment'),
                                            (b'Composition', b'composition')]),
            preserve_default=True,
        ),
    ]
