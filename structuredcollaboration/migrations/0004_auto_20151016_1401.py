# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def get_or_create_policies(apps, schema_editor):
    CollaborationPolicyRecord = apps.get_model('structuredcollaboration',
                                               'CollaborationPolicyRecord')

    valid_policies = [
        'PrivateEditorsAreOwners',
        'PublicEditorsAreOwners',
        'PrivateStudentAndFaculty',
        'CourseProtected',
        'InstructorShared',
        'InstructorManaged',
        'CourseCollaboration'
    ]

    for p in valid_policies:
        CollaborationPolicyRecord.objects.get_or_create(policy_name=p)


def deprecate_policies(apps, schema_editor):
    invalid_policies = [
        'Assignment',
        'PublicAssignment'
    ]

    CollaborationPolicyRecord = apps.get_model('structuredcollaboration',
                                               'CollaborationPolicyRecord')
    Collaboration = apps.get_model('structuredcollaboration',
                                   'Collaboration')

    course_protected = CollaborationPolicyRecord.objects.get(
        policy_name='CourseProtected')

    for p in invalid_policies:
        policies = Collaboration.objects.filter(policy_record__policy_name=p)
        policies.update(policy_record=course_protected)

    CollaborationPolicyRecord.objects.filter(
        policy_name__in=invalid_policies).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('structuredcollaboration', '0003_auto_20150509_1914'),
    ]

    operations = [
        migrations.RunPython(get_or_create_policies),
        migrations.RunPython(deprecate_policies)
    ]
