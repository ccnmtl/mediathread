# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0004_auto_20160418_1144'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseinvitation',
            name='activated_user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='courseinvitation',
            name='invited_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='invited_by',
                to=settings.AUTH_USER_MODEL),
        ),
    ]
