# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djangosherd', '0003_auto_20150721_1435'),
        ('courseaffils', '0003_auto_20160429_1353'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SequenceAsset',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='courseaffils.Course')),
                ('spine', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    blank=True, to='djangosherd.SherdNote', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SequenceMediaElement',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('start_time', models.DecimalField(
                    max_digits=12, decimal_places=5)),
                ('end_time', models.DecimalField(
                    max_digits=12, decimal_places=5)),
                ('juxtaposition', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='sequence.SequenceAsset')),
                ('media', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='djangosherd.SherdNote')),
            ],
        ),
        migrations.CreateModel(
            name='SequenceTextElement',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False,
                    auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('start_time', models.DecimalField(
                    max_digits=12, decimal_places=5)),
                ('end_time', models.DecimalField(
                    max_digits=12, decimal_places=5)),
                ('text', models.TextField()),
                ('juxtaposition', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='sequence.SequenceAsset')),
            ],
        ),
    ]
