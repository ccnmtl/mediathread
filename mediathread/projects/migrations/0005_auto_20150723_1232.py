# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def change_assignment_collaboration_type(apps, schema_editor):
    Project = apps.get_model('projects', 'Project')

    projects = Project.objects.all()
    if projects.count() > 0:
        Collaboration = apps.get_model('structuredcollaboration',
                                       'Collaboration')
        CollaborationPolicyRecord = apps.get_model('structuredcollaboration',
                                                   'CollaborationPolicyRecord')

        assignment_policy = CollaborationPolicyRecord.objects.get(
            policy_name='Assignment')
        course_protected_policy = CollaborationPolicyRecord.objects.get(
            policy_name='CourseProtected')

        colls = Collaboration.objects.filter(policy_record=assignment_policy)
        colls.update(policy_record=course_protected_policy)

        assignment_policy.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('structuredcollaboration', '0003_auto_20150509_1914'),
        ('projects', '0004_auto_20150723_1055'),
    ]

    operations = [
        migrations.RunPython(change_assignment_collaboration_type)
    ]
