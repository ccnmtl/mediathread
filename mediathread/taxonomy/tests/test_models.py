from mediathread.djangosherd.models import SherdNote
from mediathread.taxonomy.models import TermRelationship, Term
from mediathread.taxonomy.tests.factories import TaxonomyTestCase


class TermRelationshipTest(TaxonomyTestCase):

    def test_single_term_relationship(self):
        notes = SherdNote.objects.filter(asset__title='MAAP Award Reception')

        lst = TermRelationship.objects.get_for_object_list(notes)
        self.assertEquals(len(lst), 1)
        self.assertEquals(lst[0].term, Term.objects.get(name='square'))

    def test_multiple_term_relationship(self):
        notes = SherdNote.objects.filter(
            asset__title="The Armory - Home to CCNMTL'S CUMC Office")

        lst = TermRelationship.objects.get_for_object_list(notes)

        self.assertEquals(len(lst), 2)
        self.assertEquals(lst[0].term, Term.objects.get(name='red'))
        self.assertEquals(lst[1].term, Term.objects.get(name='square'))
