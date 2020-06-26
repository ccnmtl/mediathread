# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sequence', '0002_auto_20161123_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequencemediaelement',
            name='sequence_asset',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='media_elements', to='sequence.SequenceAsset'),
        ),
        migrations.AlterField(
            model_name='sequencetextelement',
            name='sequence_asset',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='text_elements', to='sequence.SequenceAsset'),
        ),
    ]
