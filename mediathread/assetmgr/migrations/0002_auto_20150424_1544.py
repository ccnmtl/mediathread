# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courseaffils', '0001_initial'),
        ('assetmgr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('url', models.CharField(max_length=1024)),
                ('thumb_url', models.CharField(max_length=1024, null=True, blank=True)),
                ('description', models.TextField()),
                ('uploader', models.BooleanField(default=False)),
                ('course', models.ForeignKey(to='courseaffils.Course')),
            ],
            options={
                'ordering': ['title'],
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='SupportedSource',
            new_name='SupportedExternalCollection',
        ),
        migrations.AlterModelOptions(
            name='supportedexternalcollection',
            options={'ordering': ['title']},
        ),
        migrations.RenameField(
            model_name='supportedexternalcollection',
            old_name='archive_url',
            new_name='url',
        ),
    ]
