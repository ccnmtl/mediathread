import factory
from mediathread.juxtapose.tests.factories import JuxtaposeAssetFactory
from mediathread.projects.models import ProjectJuxtaposeAsset
from mediathread.factories import ProjectFactory


class ProjectJuxtaposeAssetFactory(factory.DjangoModelFactory):
    class Meta:
        model = ProjectJuxtaposeAsset

    juxtapose_asset = factory.SubFactory(JuxtaposeAssetFactory)
    project = factory.SubFactory(ProjectFactory)
