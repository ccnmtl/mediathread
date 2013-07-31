from django.contrib import admin
from .models import RegistrationModel
import autocomplete_light


class RegistrationAdmin(admin.ModelAdmin):
    class Meta:
        model = RegistrationModel

    form = autocomplete_light.modelform_factory(RegistrationModel)


admin.site.register(RegistrationModel, RegistrationAdmin)
