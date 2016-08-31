# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def secure_artstor_urls(apps, schema_editor):
    Source = apps.get_model("assetmgr", "Source")
    sources = Source.objects.filter(
        url__contains='artstor', label__in=['fsiviewer', 'url', 'thumb'])

    for source in sources:
        source.url = source.url.replace('http://', 'https://')
        source.save()


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0005_auto_20150826_1437'),
    ]

    operations = [
        migrations.RunPython(secure_artstor_urls),
    ]
