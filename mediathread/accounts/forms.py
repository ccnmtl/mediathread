from django import forms

class RegistrationForm(forms.Form):
    HOW_DID_YOU_HEAR_CHOICES = (
        ('GA', 'Google Ads'),
        ('MF', 'My Friends'),
        ('MT', 'My Teacher'),
        ('MC', 'My Cat')
        )

    # form fields
    email_address = forms.EmailField()
    password = forms.CharField()
    fullname = forms.CharField()
    organization = forms.CharField()
    course_title = forms.CharField()
    how_did_you_hear_about_mediathread = forms.ChoiceField(choices = HOW_DID_YOU_HEAR_CHOICES)
    subscribe_me_to_the_mediathread_newsletter = forms.BooleanField()
    i_agree_to_terms_of_service = forms.BooleanField(required=True)



class InviteStudentsForm(forms.Form):
    student_emails = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
