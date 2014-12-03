from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from mediathread.main.models import UserSetting, UserProfile


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
