from django import forms
import autocomplete_light
from .models import CourseInformation

STUDENT_AMOUNT_CHOICES = (
        (10, '1-9'),
        (20, '10-19'),
        (50, '20-49'),
        (100, '50-99'),
        (500, '100+')
        )


class CourseForm(forms.Form):
    title = forms.CharField(required=True, label="Course title")
    student_amount = forms.ChoiceField(choices=STUDENT_AMOUNT_CHOICES,
                                       label="How many students do you expect will enroll?")
    organization = forms.CharField(widget=autocomplete_light.TextWidget('OrganizationAutocomplete'))

    class Meta:
        widget = autocomplete_light.get_widgets_dict(CourseInformation)
