# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def migrate_generic_foreign_keys(apps, schema_editor):
    TermRelationship = apps.get_model("taxonomy", "TermRelationship")
    SherdNote = apps.get_model("djangosherd", "SherdNote")

    to_delete = []

    for r in TermRelationship.objects.all():
        try:
            r.sherdnote = SherdNote.objects.get(id=r.object_id)
            r.save()
        except SherdNote.DoesNotExist:
            to_delete.append(r.id)

    TermRelationship.objects.filter(id__in=to_delete).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomy', '0005_auto_20160413_1449'),
        ('djangosherd', '0003_auto_20150721_1435')
    ]

    operations = [
        migrations.RunPython(migrate_generic_foreign_keys),
    ]
