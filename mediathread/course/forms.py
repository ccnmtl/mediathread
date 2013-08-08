from django import forms
import autocomplete_light
from .models import CourseInformation, STUDENT_AMOUNT_CHOICES


class CourseForm(forms.Form):
    title = forms.CharField(required=True, label="Course title")
    student_amount = forms.ChoiceField(choices=STUDENT_AMOUNT_CHOICES,
                                       label="How many students do you expect will enroll?")
    organization = forms.CharField(widget=autocomplete_light.TextWidget('OrganizationAutocomplete'))

    class Meta:
        widget = autocomplete_light.get_widgets_dict(CourseInformation)
