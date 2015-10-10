# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models.query_utils import Q


def update_wardenclyffe_poster_urls(apps, schema_editor):
    Source = apps.get_model("assetmgr", "Source")
    sources = Source.objects.filter(
        Q(label='poster') | Q(label='thumb') | Q(label='image'))

    new_prefix = 'https://d369ay3g98xik5.cloudfront.net/images/'
    old_prefix = 'http://wardenclyffe.ccnmtl.columbia.edu/uploads/images/'

    for source in sources.filter(url__startswith=old_prefix):
        source.url = source.url.replace(old_prefix, new_prefix)
        source.save()

    old_prefix = 'https://wardenclyffe.ccnmtl.columbia.edu/uploads/images/'
    for source in sources.filter(url__startswith=old_prefix):
        source.url = source.url.replace(old_prefix, new_prefix)
        source.save()


class Migration(migrations.Migration):

    dependencies = [
        ('assetmgr', '0003_auto_20150425_0858'),
    ]

    operations = [
        migrations.RunPython(update_wardenclyffe_poster_urls),
    ]
