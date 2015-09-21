# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('structuredcollaboration', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_comments', '__first__'),
        ('djangosherd', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussionindex',
            name='collaboration',
            field=models.ForeignKey(to='structuredcollaboration.Collaboration'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='discussionindex',
            name='comment',
            field=models.ForeignKey(to='django_comments.Comment', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='discussionindex',
            name='participant',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
