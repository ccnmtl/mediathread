from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from mediathread.main.models import (
    UserSetting, UserProfile, CourseInvitation, PanoptoIngestLogEntry)


class UserSettingAdmin(admin.ModelAdmin):
    class Meta:
        model = UserSetting

    list_display = ("user", "name", "value")
    search_fields = ("user__username",)


admin.site.register(UserSetting, UserSettingAdmin)

admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]


admin.site.register(User, UserProfileAdmin)


class CourseInvitationAdmin(admin.ModelAdmin):
    class Meta:
        model = CourseInvitation

    list_display = ('email', 'course', 'invited_by',
                    'invited_at', 'accepted_at')
    search_fields = ('email',)


admin.site.register(CourseInvitation, CourseInvitationAdmin)


class PanoptoIngestLogEntryAdmin(admin.ModelAdmin):
    class Meta:
        model = PanoptoIngestLogEntry

    list_display = ('course', 'session_id', 'level',
                    'message', 'created_at')
    list_filter = ('level',)

    search_fields = ('course__title', 'session_id')


admin.site.register(PanoptoIngestLogEntry, PanoptoIngestLogEntryAdmin)
