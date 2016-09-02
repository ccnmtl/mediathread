# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_external_collections(apps, schema_editor):
    ExternalCollection = apps.get_model('assetmgr', 'ExternalCollection')
    qs = ExternalCollection.objects.filter(
        thumb_url__startswith='/media/img/thumbs/')

    for ec in qs:
        ec.thumb_url = ec.thumb_url.replace('/media/img/thumbs/',
                                            'img/thumbs/')
        ec.save()

    SuggestedExternalCollection = apps.get_model('assetmgr',
                                                 'SuggestedExternalCollection')
    qs = SuggestedExternalCollection.objects.filter(
        thumb_url__startswith='/media/img/thumbs/')

    for sec in qs:
        sec.thumb_url = sec.thumb_url.replace('/media/img/thumbs/',
                                              'img/thumbs/')
        sec.save()


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0006_auto_20160831_1348'),
    ]

    operations = [
        migrations.RunPython(update_external_collections),
    ]
