# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_auto_20161026_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='custom_instructions_1',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='custom_instructions_2',
            field=models.CharField(max_length=140, null=True, blank=True),
        ),
    ]
