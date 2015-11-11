# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('structuredcollaboration', '0004_auto_20151016_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collaborationpolicyrecord',
            name='policy_name',
            field=models.CharField(max_length=512, db_index=True),
        ),
    ]
