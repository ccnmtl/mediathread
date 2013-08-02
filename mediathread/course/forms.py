from django import forms
import autocomplete_light


class CourseForm(forms.Form):
    STUDENT_AMOUNT_CHOICES = (
        (10, '1-9'),
        (20, '10-19'),
        (50, '20-49'),
        (100, '50-99'),
        (500, '100+')
    )
    title = forms.CharField(required=True)
    organization = forms.CharField(widget=autocomplete_light.TextWidget('OrganizationAutocomplete'))
    student_amount = forms.ChoiceField(choices=STUDENT_AMOUNT_CHOICES)
