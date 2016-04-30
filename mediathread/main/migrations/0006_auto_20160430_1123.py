# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20160430_0901'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courseinvitation',
            old_name='activated_at',
            new_name='accepted_at',
        ),
        migrations.RenameField(
            model_name='courseinvitation',
            old_name='activated_user',
            new_name='accepted_user',
        ),
    ]
