# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0006_auto_20160413_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vocabulary',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='vocabulary',
            name='object_id',
        ),
        migrations.AlterField(
            model_name='termrelationship',
            name='sherdnote',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='djangosherd.SherdNote'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='vocabulary',
            name='course',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='courseaffils.Course'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='termrelationship',
            unique_together=set([('term', 'sherdnote')]),
        ),
        migrations.RemoveField(
            model_name='termrelationship',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='termrelationship',
            name='object_id',
        ),
    ]
