# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def delete_orphan_collaborations(apps, schema_editor):
    Collaboration = apps.get_model('structuredcollaboration', 'Collaboration')

    qs = Collaboration.objects.filter(content_type__isnull=True,
                                      object_pk__isnull=True)
    qs.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('structuredcollaboration', '0004_auto_20151016_1401'),
    ]

    operations = [
         migrations.RunPython(delete_orphan_collaborations)
    ]
