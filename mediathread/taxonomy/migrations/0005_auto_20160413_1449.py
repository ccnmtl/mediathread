# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_generic_foreign_keys(apps, schema_editor):
    Vocabulary = apps.get_model("taxonomy", "Vocabulary")
    Course = apps.get_model("courseaffils", "Course")

    to_delete = []
    for v in Vocabulary.objects.all():
        try:
            v.course = Course.objects.get(id=v.object_id)
            v.save()
        except Course.DoesNotExist:
            to_delete.append(v.id)

    Vocabulary.objects.filter(id__in=to_delete).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0004_auto_20160413_1447'),
        ('courseaffils', '0002_auto_20160316_1223')
    ]

    operations = [
        migrations.RunPython(migrate_generic_foreign_keys),
    ]
