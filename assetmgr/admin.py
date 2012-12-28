from mediathread.assetmgr.models import Asset, Source, SupportedSource
from django.contrib import admin


class AssetAdmin(admin.ModelAdmin):
    class Meta:
        model = Asset

    change_form_template = "assetmgr/admin_change_form.html"
    search_fields = ("title", "course__title", "source__url",)
    list_display = ("title", "id", "course", "added", "modified", "active")


class SourceAdmin(admin.ModelAdmin):
    def course_title(self, obj):
        return obj.asset.course.title

    class Meta:
        model = Source

    search_fields = ("label", "asset__title", "url", "asset__course__title")
    list_display = ("label", "asset", "course_title", "primary")

admin.site.register(Asset, AssetAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(SupportedSource)
