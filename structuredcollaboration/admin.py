from models import Collaboration, CollaborationPolicyRecord
from django.contrib import admin

admin.site.register(CollaborationPolicyRecord)


class CollaborationAdmin(admin.ModelAdmin):
    search_fields = ('title', 'slug', )
    list_display = ('title', 'group', 'user', '_policy', 'slug', )

admin.site.register(Collaboration, CollaborationAdmin)
