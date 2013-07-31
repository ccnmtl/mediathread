import autocomplete_light
from .models import RegistrationModel

autocomplete_light.register(RegistrationModel,
        search_fields = ['^organization'],
        autocomplete_js_attributes={},
        )
