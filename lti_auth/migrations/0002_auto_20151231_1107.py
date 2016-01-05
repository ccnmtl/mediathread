# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('lti_auth', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lticoursecontext',
            name='lms_context_id',
        ),
        migrations.AddField(
            model_name='lticoursecontext',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
