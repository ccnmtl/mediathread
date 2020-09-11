from mediathread.taxonomy.models import Vocabulary, Term, TermRelationship
from django.contrib import admin


def term_vocabulary_name(obj):
    return obj.vocabulary.display_name


term_vocabulary_name.short_description = 'Vocabulary'


class TermAdmin(admin.ModelAdmin):
    class Meta:
        model = Term

    search_fields = ("display_name", "vocabulary__display_name")
    list_display = ("display_name",
                    term_vocabulary_name)


admin.site.register(Term, TermAdmin)
admin.site.register(TermRelationship)


class VocabularyAdmin(admin.ModelAdmin):
    class Meta:
        model = Vocabulary

    search_fields = ("display_name",)
    list_display = ("display_name", "course")


admin.site.register(Vocabulary, VocabularyAdmin)
