# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='term',
            name='display_name',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='term',
            name='name',
            field=models.SlugField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vocabulary',
            name='display_name',
            field=models.CharField(max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vocabulary',
            name='name',
            field=models.SlugField(max_length=100),
            preserve_default=True,
        ),
    ]
