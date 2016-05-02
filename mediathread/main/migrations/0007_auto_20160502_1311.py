# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20160430_1123'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='affil',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='affil',
            name='user',
        ),
        migrations.DeleteModel(
            name='Affil',
        ),
    ]
