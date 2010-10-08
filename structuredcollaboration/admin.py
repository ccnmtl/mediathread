from models import Collaboration,CollaborationPolicyRecord
from django.contrib import admin

admin.site.register(CollaborationPolicyRecord)

class CollaborationAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    list_display = ('title','group','user','_policy',)

admin.site.register(Collaboration, CollaborationAdmin)
