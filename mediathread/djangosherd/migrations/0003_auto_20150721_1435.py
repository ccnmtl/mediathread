# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangosherd', '0002_auto_20150327_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sherdnote',
            name='added',
            field=models.DateTimeField(auto_now_add=True,
                                       verbose_name=b'date created'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sherdnote',
            name='modified',
            field=models.DateTimeField(auto_now=True,
                                       verbose_name=b'date modified'),
            preserve_default=True,
        ),
    ]
