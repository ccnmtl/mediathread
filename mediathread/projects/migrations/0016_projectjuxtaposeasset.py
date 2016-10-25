# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('juxtapose', '0002_auto_20161018_1601'),
        ('projects', '0015_auto_20161019_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectJuxtaposeAsset',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('juxtapose_asset',
                 models.ForeignKey(to='juxtapose.JuxtaposeAsset')),
                ('project', models.ForeignKey(to='projects.Project')),
            ],
        ),
    ]
