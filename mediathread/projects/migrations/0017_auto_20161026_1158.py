# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sequence', '0001_initial'),
        ('projects', '0016_projectjuxtaposeasset'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectSequenceAsset',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(to='projects.Project')),
                ('sequence_asset', models.ForeignKey(
                    to='sequence.SequenceAsset')),
            ],
        ),
        migrations.RemoveField(
            model_name='projectjuxtaposeasset',
            name='juxtapose_asset',
        ),
        migrations.RemoveField(
            model_name='projectjuxtaposeasset',
            name='project',
        ),
        migrations.DeleteModel(
            name='ProjectJuxtaposeAsset',
        ),
    ]
