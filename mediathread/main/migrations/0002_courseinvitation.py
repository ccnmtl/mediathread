# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('courseaffils', '0002_auto_20160316_1223'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseInvitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('activated_at', models.DateTimeField(null=True)),
                ('invited_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='courseaffils.Course')),
                ('invited_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
