import factory
from factory.django import DjangoModelFactory
from mediathread.sequence.tests.factories import SequenceAssetFactory
from mediathread.projects.models import ProjectSequenceAsset
from mediathread.factories import ProjectFactory


class ProjectSequenceAssetFactory(DjangoModelFactory):
    class Meta:
        model = ProjectSequenceAsset

    sequence_asset = factory.SubFactory(SequenceAssetFactory)
    project = factory.SubFactory(ProjectFactory)
