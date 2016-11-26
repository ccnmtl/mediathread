# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sequence', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sequencemediaelement',
            old_name='juxtaposition',
            new_name='sequence_asset',
        ),
        migrations.RenameField(
            model_name='sequencetextelement',
            old_name='juxtaposition',
            new_name='sequence_asset',
        ),
    ]
