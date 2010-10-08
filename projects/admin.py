from models import Project
from django.contrib import admin

class ProjectAdmin(admin.ModelAdmin):
    search_fields = ("title","participants__last_name",)
    list_display = ("title","course","modified","submitted","id")
    

admin.site.register(Project,ProjectAdmin)
