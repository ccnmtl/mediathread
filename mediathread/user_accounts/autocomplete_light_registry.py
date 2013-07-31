import autocomplete_light
from .models import RegistrationModel, OrganizationModel

class OrganizationAutocomplete(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes = {
            'placeholder': 'Organization name...',
            }

    search_fields = ['name']




autocomplete_light.register(OrganizationModel, OrganizationAutocomplete, name="OrganizationAutocomplete")
