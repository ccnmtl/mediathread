from structuredcollaboration.models import (
    Collaboration, CollaborationPolicyRecord
)
from django.contrib import admin

admin.site.register(CollaborationPolicyRecord)


class CollaborationAdmin(admin.ModelAdmin):
    search_fields = ('title', 'slug', )
    list_display = ('title', 'group', 'user', 'policy_record', 'slug')
    readonly_fields = (
        'user', 'policy_record', 'group', 'created_at', 'updated_at'
    )
    raw_id_fields = ('user', 'policy_record', 'group')
    fields = (
        'title', 'group', 'user', 'policy_record', 'slug',
        'created_at', 'updated_at'
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(
            CollaborationAdmin, self).get_search_results(
            request, queryset, search_term)
        return queryset.distinct(), True


admin.site.register(Collaboration, CollaborationAdmin)
