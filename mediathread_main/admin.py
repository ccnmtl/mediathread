from django.contrib import admin
from mediathread.mediathread_main.models import UserSetting


class UserSettingAdmin(admin.ModelAdmin):
    class Meta:
        model = UserSetting

    list_display = ("user", "name", "value")


admin.site.register(UserSetting, UserSettingAdmin)
