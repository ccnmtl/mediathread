# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangosherd', '0003_auto_20150721_1435'),
        ('courseaffils', '0002_auto_20160316_1223'),
        ('taxonomy', '0003_auto_20150728_0730'),
    ]

    operations = [
        migrations.AddField(
            model_name='termrelationship',
            name='sherdnote',
            field=models.ForeignKey(to='djangosherd.SherdNote', null=True),
        ),
        migrations.AddField(
            model_name='vocabulary',
            name='course',
            field=models.ForeignKey(to='courseaffils.Course', null=True),
        ),
    ]
