# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('url', models.CharField(max_length=1024)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='SupportedSource',
            new_name='SupportedExternalCollection',
        ),
        migrations.RenameField(
            model_name='supportedexternalcollection',
            old_name='archive_url',
            new_name='url',
        ),
    ]
