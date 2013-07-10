from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from django.contrib import admin

admin.site.register(Vocabulary)
admin.site.register(Term)
admin.site.register(TermRelationship)
