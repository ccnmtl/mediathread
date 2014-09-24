import factory
from mediathread.assetmgr.model import Asset


class AssetFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Asset
