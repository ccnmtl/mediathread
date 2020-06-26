# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import tagging.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('range1', models.FloatField(default=None, null=True)),
                ('range2', models.FloatField(default=None, null=True)),
                ('annotation_data', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DiscussionIndex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('asset', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='discussion_references', to='assetmgr.Asset', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SherdNote',
            fields=[
                ('annotation_ptr', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True, auto_created=True, primary_key=True, serialize=False, to='djangosherd.Annotation')),
                ('title', models.CharField(max_length=1024, null=True, blank=True)),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('body', models.TextField(null=True, blank=True)),
                ('added', models.DateTimeField(verbose_name=b'date created', editable=False)),
                ('modified', models.DateTimeField(verbose_name=b'date modified', editable=False)),
                ('asset', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sherdnote_set', to='assetmgr.Asset')),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=('djangosherd.annotation',),
        ),
    ]
