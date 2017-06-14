# pylint: disable-msg=R0904
from django.contrib import admin

from mediathread.assetmgr.models import (Asset, ExternalCollection, Source,
                                         SuggestedExternalCollection)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    class Meta:
        model = Asset

    change_form_template = "assetmgr/admin_change_form.html"
    search_fields = ("title", "course__title", "source__url",)
    list_display = ("title", "id", "course", "added", "modified", "active")


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):

    def queryset(self, request):
        return super(SourceAdmin, self).queryset(
            request).select_related('asset', 'asset__course')

    def course_title(self, obj):
        return obj.asset.course.title

    class Meta:
        model = Source

    search_fields = ("label", "asset__title", "url", "asset__course__title")
    list_display = ("label", "asset", "course_title", "primary")
    raw_id_fields = ("asset",)
    readonly_fields = ("asset",)


@admin.register(ExternalCollection)
class ExternalCollectionAdmin(admin.ModelAdmin):
    class Meta:
        model = ExternalCollection

    search_fields = ("title", "course__title")
    list_display = ("title", "course", "uploader")


admin.site.register(SuggestedExternalCollection)
