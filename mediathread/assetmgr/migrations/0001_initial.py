# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courseaffils', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name=b'date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name=b'date modified')),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=1024)),
                ('metadata_blob', models.TextField(help_text=b'Be careful, this is a JSON blob and NOT a place to enter the description, etc, and is easy to format incorrectly. Make sure not to add any "\'s.', blank=True)),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='asset_set', to='courseaffils.Course')),
            ],
            options={
                'permissions': (('can_upload_for', 'Can upload assets for others'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=64)),
                ('url', models.CharField(max_length=4096)),
                ('primary', models.BooleanField(default=False)),
                ('media_type', models.CharField(default=None, max_length=64, null=True)),
                ('size', models.PositiveIntegerField(default=0)),
                ('height', models.PositiveSmallIntegerField(default=0)),
                ('width', models.PositiveSmallIntegerField(default=0)),
                ('modified', models.DateTimeField(auto_now=True, verbose_name=b'date modified')),
                ('asset', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='assetmgr.Asset')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SupportedSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('archive_url', models.CharField(max_length=1024)),
                ('thumb_url', models.CharField(max_length=1024)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
