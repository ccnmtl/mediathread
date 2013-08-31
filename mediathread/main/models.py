from django.contrib.auth.models import User
from django.db import models


class UserSetting(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    @classmethod
    def get_setting(cls, user, setting_id, default_value):
        try:
            user_setting = UserSetting.objects.get(user=user, name=setting_id)

            if (user_setting.value == 'True' or
                    user_setting.value == 'true'):
                return True
            elif (user_setting.value == 'False' or
                    user_setting.value == 'false'):
                return False
            else:
                return user_setting.value
        except:
            return default_value

    @classmethod
    def set_setting(cls, user, setting_id, value):
        try:
            user_setting = UserSetting.objects.get(user=user, name=setting_id)
            user_setting.value = str(value)
            user_setting.save()
        except:
            UserSetting.objects.create(user=user, name=setting_id, value=value)
