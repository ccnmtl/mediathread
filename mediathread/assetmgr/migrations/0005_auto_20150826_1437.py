# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0004_auto_20150713_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='primary',
            field=models.BooleanField(default=False, db_index=True),
            preserve_default=True,
        ),
    ]
