# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_auto_20161101_1307'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='projectsequenceasset',
            unique_together=set([('sequence_asset', 'project')]),
        ),
    ]
