# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-16 17:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courseaffils', '0004_auto_20170623_1231'),
        ('main', '0007_auto_20160502_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='PanoptoIngestLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.TextField()),
                ('level', models.IntegerField()),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courseaffils.Course')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
