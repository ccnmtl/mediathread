# pylint: disable-msg=R0904
from django.contrib import admin

from mediathread.assetmgr.models import (Asset, Source,
                                         SupportedExternalCollection,
                                         ExternalCollection)


class AssetAdmin(admin.ModelAdmin):
    class Meta:
        model = Asset

    change_form_template = "assetmgr/admin_change_form.html"
    search_fields = ("title", "course__title", "source__url",)
    list_display = ("title", "id", "course", "added", "modified", "active")


class SourceAdmin(admin.ModelAdmin):
    def queryset(self, request):
        return super(SourceAdmin, self).queryset(
            request).select_related('asset')

    def course_title(self, obj):
        return obj.asset.course.title

    class Meta:
        model = Source

    search_fields = ("label", "asset__title", "url", "asset__course__title")
    list_display = ("label", "asset", "course_title", "primary")


class ExternalCollectionAdmin(admin.ModelAdmin):
    class Meta:
        model = ExternalCollection

    search_fields = ("title", "course__title")
    list_display = ("title", "course", "uploader")

admin.site.register(Asset, AssetAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(ExternalCollection, ExternalCollectionAdmin)
admin.site.register(SupportedExternalCollection)
