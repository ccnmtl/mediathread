# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sequence', '0003_auto_20161123_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='sequenceasset',
            name='spine_volume',
            field=models.PositiveSmallIntegerField(
                default=80,
                validators=[django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='sequencemediaelement',
            name='volume',
            field=models.PositiveSmallIntegerField(
                default=80,
                validators=[django.core.validators.MaxValueValidator(100)]),
        ),
    ]
