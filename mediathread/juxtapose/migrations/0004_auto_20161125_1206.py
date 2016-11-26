# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('juxtapose', '0003_remove_juxtaposeasset_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='juxtaposeasset',
            name='author',
        ),
        migrations.RemoveField(
            model_name='juxtaposeasset',
            name='course',
        ),
        migrations.RemoveField(
            model_name='juxtaposeasset',
            name='spine',
        ),
        migrations.RemoveField(
            model_name='juxtaposemediaelement',
            name='juxtaposition',
        ),
        migrations.RemoveField(
            model_name='juxtaposemediaelement',
            name='media',
        ),
        migrations.RemoveField(
            model_name='juxtaposetextelement',
            name='juxtaposition',
        ),
        migrations.DeleteModel(
            name='JuxtaposeAsset',
        ),
        migrations.DeleteModel(
            name='JuxtaposeMediaElement',
        ),
        migrations.DeleteModel(
            name='JuxtaposeTextElement',
        ),
    ]
