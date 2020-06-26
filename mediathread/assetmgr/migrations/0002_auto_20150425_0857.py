# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courseaffils', '0001_initial'),
        ('assetmgr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalCollection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('url', models.CharField(max_length=1024)),
                ('thumb_url', models.CharField(max_length=1024, null=True,
                                               blank=True)),
                ('description', models.TextField()),
                ('uploader', models.BooleanField(default=False)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='courseaffils.Course')),
            ],
            options={
                'ordering': ['title'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='externalcollection',
            unique_together=set([('title', 'course')]),
        ),
        migrations.RenameModel(
            old_name='SupportedSource',
            new_name='SuggestedExternalCollection',
        ),
        migrations.AlterModelOptions(
            name='suggestedexternalcollection',
            options={'ordering': ['title']},
        ),
        migrations.RenameField(
            model_name='suggestedexternalcollection',
            old_name='archive_url',
            new_name='url',
        ),
        migrations.AlterField(
            model_name='suggestedexternalcollection',
            name='title',
            field=models.CharField(max_length=1024, unique=True)
        ),
    ]
