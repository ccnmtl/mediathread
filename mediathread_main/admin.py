from django.contrib.auth.admin import UserAdmin

UserAdmin.filter_horizontal = ('user_permissions', 'groups')