# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('juxtapose', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='juxtaposemediaelement',
            name='end_time',
            field=models.DecimalField(max_digits=12, decimal_places=5),
        ),
        migrations.AlterField(
            model_name='juxtaposemediaelement',
            name='start_time',
            field=models.DecimalField(max_digits=12, decimal_places=5),
        ),
        migrations.AlterField(
            model_name='juxtaposetextelement',
            name='end_time',
            field=models.DecimalField(max_digits=12, decimal_places=5),
        ),
        migrations.AlterField(
            model_name='juxtaposetextelement',
            name='start_time',
            field=models.DecimalField(max_digits=12, decimal_places=5),
        ),
    ]
