# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0004_auto_20150713_1146'),
        ('projects', '0005_auto_20150723_1232'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignmentItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('asset', models.ForeignKey(to='assetmgr.Asset')),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
