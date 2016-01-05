# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lti_auth', '0003_auto_20151231_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='lticoursecontext',
            name='enable',
            field=models.BooleanField(default=False),
        ),
    ]
