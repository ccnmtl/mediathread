from models import Asset, Source
from django.contrib import admin

class AssetAdmin(admin.ModelAdmin):
    class Meta:
        model = Asset
        
    change_form_template="assetmgr/admin_change_form.html"

admin.site.register(Asset,AssetAdmin)
admin.site.register(Source)

