# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('structuredcollaboration', '0002_auto_20150509_1801'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collaborationpolicyrecord',
            name='policy_name',
            field=models.CharField(max_length=512),
            preserve_default=True,
        ),
    ]
