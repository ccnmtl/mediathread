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
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('body', models.TextField(blank=True)),
                ('submitted', models.BooleanField(default=False)),
                ('feedback', models.TextField(null=True, blank=True)),
                ('modified',
                 models.DateTimeField(auto_now=True,
                                      verbose_name=b'date modified')),
                ('due_date', models.DateTimeField(null=True,
                                                  verbose_name=b'due date',
                                                  blank=True)),
                ('ordinality', models.IntegerField(default=-1)),
                ('author', models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='project_set',
                    to='courseaffils.Course')),
                ('participants',
                 models.ManyToManyField(related_name='projects',
                                        null=True, verbose_name=b'Authors',
                                        to=settings.AUTH_USER_MODEL,
                                        blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=1024)),
                ('body', models.TextField(blank=True)),
                ('submitted', models.BooleanField(default=False)),
                ('feedback', models.TextField(null=True, blank=True)),
                ('modified',
                 models.DateTimeField(auto_now=True,
                                      verbose_name=b'date modified')),
                ('due_date', models.DateTimeField(null=True,
                                                  verbose_name=b'due date',
                                                  blank=True)),
                ('ordinality', models.IntegerField(default=-1)),
                ('author', models.IntegerField()),
                ('course', models.IntegerField()),
                ('versioned_id', models.IntegerField()),
                ('version_number', models.IntegerField()),
                ('change_time', models.DateTimeField(auto_now_add=True)),
                ('change_type', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
