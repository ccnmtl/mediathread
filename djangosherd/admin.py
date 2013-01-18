from models import SherdNote
from django.contrib import admin


class SherdNoteAdmin(admin.ModelAdmin):
    search_fields = ("title", "author__last_name", "asset__title")
    list_display = ("title", "asset", "author", "modified", "added", "id")


admin.site.register(SherdNote, SherdNoteAdmin)
