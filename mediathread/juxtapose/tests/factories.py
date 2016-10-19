import factory
from factory import fuzzy
from mediathread.factories import (
    UserFactory, CourseFactory, SherdNoteFactory
)
from mediathread.juxtapose.models import (
    JuxtaposeAsset, JuxtaposeMediaElement, JuxtaposeTextElement,
)


class JuxtaposeAssetFactory(factory.DjangoModelFactory):
    class Meta:
        model = JuxtaposeAsset

    author = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    title = fuzzy.FuzzyText()


class JuxtaposeMediaElementFactory(factory.DjangoModelFactory):
    class Meta:
        model = JuxtaposeMediaElement

    juxtaposition = factory.SubFactory(JuxtaposeAssetFactory)
    start_time = fuzzy.FuzzyDecimal(0.0, 3.0)
    end_time = fuzzy.FuzzyDecimal(3.01, 6.0)
    media = factory.SubFactory(SherdNoteFactory)


class JuxtaposeTextElementFactory(factory.DjangoModelFactory):
    class Meta:
        model = JuxtaposeTextElement

    juxtaposition = factory.SubFactory(JuxtaposeAssetFactory)
    start_time = fuzzy.FuzzyDecimal(5.0, 105.0)
    end_time = fuzzy.FuzzyDecimal(1000.01, 6000.0)
    text = fuzzy.FuzzyText()
