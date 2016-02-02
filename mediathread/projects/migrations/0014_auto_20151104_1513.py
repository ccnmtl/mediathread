# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def delete_orphan_collaborations(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    Collaboration = apps.get_model('structuredcollaboration', 'Collaboration')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    try:
        ctype = ContentType.objects.get(model='project', app_label='projects')

        to_delete = []
        for c in Collaboration.objects.filter(content_type=ctype):
            try:
                Project.objects.get(id=int(c.object_pk))
            except Project.DoesNotExist:
                to_delete.append(c.id)

        Collaboration.objects.filter(id__in=to_delete).delete()
    except ContentType.DoesNotExist:
        pass  # skip this migration during unit tests


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_auto_20151021_1438'),
        ('structuredcollaboration', '0004_auto_20151016_1401'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
         migrations.RunPython(delete_orphan_collaborations)
    ]
