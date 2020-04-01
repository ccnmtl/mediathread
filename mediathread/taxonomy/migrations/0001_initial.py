# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField()),
                ('display_name', models.CharField(max_length=20)),
                ('description', models.CharField(max_length=256, null=True, blank=True)),
                ('ordinality', models.IntegerField(default=0, null=True, blank=True)),
            ],
            options={
                'ordering': ['display_name', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TermRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='contenttypes.ContentType')),
                ('term', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='taxonomy.Term')),
            ],
            options={
                'ordering': ['term__display_name', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vocabulary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField()),
                ('display_name', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('single_select', models.BooleanField(default=False)),
                ('onomy_url', models.TextField(null=True, blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['display_name', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='termrelationship',
            unique_together=set([('term', 'content_type', 'object_id')]),
        ),
        migrations.AddField(
            model_name='term',
            name='vocabulary',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='taxonomy.Vocabulary'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='term',
            unique_together=set([('name', 'vocabulary')]),
        ),
    ]
