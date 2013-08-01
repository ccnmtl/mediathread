from django.contrib import admin
from .models import RegistrationModel, OrganizationModel
import autocomplete_light


class RegistrationAdmin(admin.ModelAdmin):
    class Meta:
        model = RegistrationModel

    form = autocomplete_light.modelform_factory(RegistrationModel)

class OrganizationAdmin(admin.ModelAdmin):
    class Meta:
        model = OrganizationModel



admin.site.register(RegistrationModel, RegistrationAdmin)
admin.site.register(OrganizationModel, OrganizationAdmin)
