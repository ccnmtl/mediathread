# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Min


def populate_date_submitted(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')
    ProjectVersion = apps.get_model('projects', 'ProjectVersion')

    # for all existing projects which are submitted ~14,608
    qs = Project.objects.filter(submitted=True, project_type='composition')
    qs = qs.values_list('id', flat=True)

    # find the date/time submitted.
    # equal to the 1st version change where submitted = True
    # so, aggregate the min change_time where submitted=True
    versions = ProjectVersion.objects.filter(
        submitted=True, versioned_id__in=qs)
    versions = versions.values(
        'versioned_id').distinct().annotate(min_change_time=Min('change_time'))

    # populate the date/time submitted
    for v in versions:
        p = Project.objects.get(id=v['versioned_id'])
        p.date_submitted = v['min_change_time']
        p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_auto_20150831_1631'),
    ]

    operations = [
         migrations.RunPython(populate_date_submitted)
    ]
