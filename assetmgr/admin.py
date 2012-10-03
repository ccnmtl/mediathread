from mediathread.assetmgr.models import Asset, Source, SupportedSource
from django.contrib import admin

class AssetAdmin(admin.ModelAdmin):
    class Meta:
        model = Asset
        
    change_form_template="assetmgr/admin_change_form.html"
    search_fields = ("title","course__title","source__url",)
    list_display = ("title","id","course","added","modified","active")

admin.site.register(Asset,AssetAdmin)
admin.site.register(Source)
admin.site.register(SupportedSource)

