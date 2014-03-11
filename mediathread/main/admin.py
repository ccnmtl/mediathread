from django.contrib import admin
from mediathread.main.models import UserSetting


class UserSettingAdmin(admin.ModelAdmin):
    class Meta:
        model = UserSetting

    list_display = ("user", "name", "value")
    search_fields = ("user__username",)


admin.site.register(UserSetting, UserSettingAdmin)
