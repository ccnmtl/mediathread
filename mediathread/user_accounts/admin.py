from django.contrib import admin
from .models import RegistrationModel


class RegistrationAdmin(admin.ModelAdmin):
    class Meta:
        model = RegistrationModel


admin.site.register(RegistrationModel, RegistrationAdmin)
