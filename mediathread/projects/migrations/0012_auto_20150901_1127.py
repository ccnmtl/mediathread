# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_auto_20150831_1632'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='submitted',
        ),
        migrations.RemoveField(
            model_name='projectversion',
            name='submitted',
        ),
    ]
