# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import migrations
from django.db.models.query_utils import Q


def metadata(archive):
    if archive.metadata_blob:
        try:
            return json.loads(str(archive.metadata_blob))
        except ValueError:
            pass
    return {}


def refactor_archives(apps, schema_editor):
    Asset = apps.get_model("assetmgr", "Asset")
    ExternalCollection = apps.get_model("assetmgr", "ExternalCollection")
    Source = apps.get_model("assetmgr", "Source")
    SherdNote = apps.get_model("djangosherd", "SherdNote")

    archives = Asset.objects.filter(Q(source__primary=True) &
                                    Q(source__label='archive'))

    for archive in archives:
        exc = ExternalCollection()
        exc.title = archive.title
        exc.course = archive.course

        the_metadata = metadata(archive)
        description = the_metadata.get('description', [''])
        exc.description = description[0]

        value = the_metadata.get('upload', [0])
        try:
            is_uploader = int(value[0])
        except ValueError:
            is_uploader = 0
            pass
        exc.uploader = is_uploader == 1

        source = Source.objects.get(asset=archive, primary=True)
        exc.url = source.url

        try:
            source = Source.objects.get(asset=archive,
                                        primary=False, label="thumb")
            exc.thumb_url = source.url
        except Source.DoesNotExist:
            pass  # that's okay

        exc.save()

        notes = SherdNote.objects.filter(asset=archive)
        notes.delete()

    archives.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0002_auto_20150425_0857'),
        ('courseaffils', '0001_initial'),
        ('djangosherd', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(refactor_archives),
    ]
