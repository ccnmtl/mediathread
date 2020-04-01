# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djangosherd', '0003_auto_20150721_1435'),
        ('projects', '0007_auto_20150808_0826'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True,
                                        primary_key=True)),
                ('annotation', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='djangosherd.SherdNote')),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='projects.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='project',
            name='response_view_policy',
            field=models.TextField(
                default=b'always',
                choices=[(b'never', b'Viewable by instructor only'),
                         (b'always', b'Viewable by all'),
                         (b'submitted', b'Viewable by other submitters')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectversion',
            name='response_view_policy',
            field=models.TextField(
                default=b'always',
                choices=[(b'never', b'Viewable by instructor only'),
                         (b'always', b'Viewable by all'),
                         (b'submitted', b'Viewable by other submitters')]),
            preserve_default=True,
        ),
    ]
