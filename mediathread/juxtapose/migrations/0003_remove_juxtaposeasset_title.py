# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('juxtapose', '0002_auto_20161018_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='juxtaposeasset',
            name='title',
        ),
    ]
