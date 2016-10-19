# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_auto_20151104_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='response_view_policy',
            field=models.TextField(
                default=b'always',
                choices=[
                    (b'never', b'Never - Responses visible only to '
                     b'instructors'),
                    (b'always', b'Always - Response not required to view '
                     b'other student responses'),
                    (b'submitted', b'After Submission - Response required to '
                     b'view other student responses before due date. All '
                     b'responses visible after assignment due date passes.')]),
        ),
    ]
