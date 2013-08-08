from django.contrib import admin
from .models import CourseInformation


class CourseInformationAdmin(admin.ModelAdmin):
    class Meta:
        model = CourseInformation

admin.site.register(CourseInformation, CourseInformationAdmin)
