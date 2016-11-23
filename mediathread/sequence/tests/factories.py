import factory
from factory import fuzzy
from mediathread.factories import (
    UserFactory, CourseFactory, SherdNoteFactory
)
from mediathread.sequence.models import (
    SequenceAsset, SequenceMediaElement, SequenceTextElement,
)


class SequenceAssetFactory(factory.DjangoModelFactory):
    class Meta:
        model = SequenceAsset

    author = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)


class SequenceMediaElementFactory(factory.DjangoModelFactory):
    class Meta:
        model = SequenceMediaElement

    sequence_asset = factory.SubFactory(SequenceAssetFactory)
    start_time = fuzzy.FuzzyDecimal(0.0, 3.0)
    end_time = fuzzy.FuzzyDecimal(3.01, 6.0)
    media = factory.SubFactory(SherdNoteFactory)


class SequenceTextElementFactory(factory.DjangoModelFactory):
    class Meta:
        model = SequenceTextElement

    sequence_asset = factory.SubFactory(SequenceAssetFactory)
    start_time = fuzzy.FuzzyDecimal(5.0, 105.0)
    end_time = fuzzy.FuzzyDecimal(1000.01, 6000.0)
    text = fuzzy.FuzzyText()
