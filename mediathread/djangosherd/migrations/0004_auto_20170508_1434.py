# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('djangosherd', '0003_auto_20150721_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sherdnote',
            name='tags',
            field=tagging.fields.TagField(max_length=1024, blank=True),
        ),
    ]
