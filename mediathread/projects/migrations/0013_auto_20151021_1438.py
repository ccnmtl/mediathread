# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0012_auto_20150901_1127'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProjectVersion',
        ),
        migrations.AlterField(
            model_name='project',
            name='participants',
            field=models.ManyToManyField(related_name='projects',
                                         verbose_name=b'Authors',
                                         to=settings.AUTH_USER_MODEL,
                                         blank=True),
        ),
    ]
