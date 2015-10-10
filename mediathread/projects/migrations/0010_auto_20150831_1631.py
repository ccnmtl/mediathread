# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20150827_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='date_submitted',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectversion',
            name='date_submitted',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
