# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def classify_projects(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')

    projects = Project.objects.all()
    if projects.count() > 0:
        Collaboration = apps.get_model('structuredcollaboration',
                                       'Collaboration')
        ContentType = apps.get_model('contenttypes', 'ContentType')
        ctype = ContentType.objects.get(name='project', app_label='projects')

        for project in Project.objects.all():
            project.project_type = 'composition'
            try:
                collaboration = Collaboration.objects.get(
                    content_type=ctype, object_pk=str(project.id))

                if collaboration.policy_record.policy_name == 'Assignment':
                    project.project_type = 'assignment'
            except Collaboration.DoesNotExist:
                pass  # private projects do not always have collaborations.

            project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('structuredcollaboration', '0003_auto_20150509_1914'),
        ('projects', '0003_auto_20150723_0845'),
    ]

    operations = [
        migrations.RunPython(classify_projects),
    ]
