from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from django.contrib import admin


def term_vocabulary_name(obj):
    return obj.vocabulary.display_name


term_vocabulary_name.short_description = 'Vocabulary'


def term_vocabulary_related_name(obj):
    return obj.vocabulary.content_object.__unicode__()


term_vocabulary_related_name.short_description = 'Related To'


class TermAdmin(admin.ModelAdmin):
    class Meta:
        model = Term

    search_fields = ("display_name", "vocabulary__display_name")
    list_display = ("display_name",
                    term_vocabulary_name,
                    term_vocabulary_related_name)


admin.site.register(Term, TermAdmin)
admin.site.register(TermRelationship)


def vocabulary_related_name(obj):
    return obj.content_object.__unicode__()


vocabulary_related_name.short_description = 'Related To'


class VocabularyAdmin(admin.ModelAdmin):
    class Meta:
        model = Vocabulary

    search_fields = ("display_name",)
    list_display = ("display_name", vocabulary_related_name)


admin.site.register(Vocabulary, VocabularyAdmin)
