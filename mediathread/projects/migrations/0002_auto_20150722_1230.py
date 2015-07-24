# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='feedback',
        ),
        migrations.RemoveField(
            model_name='projectversion',
            name='feedback',
        ),
    ]
