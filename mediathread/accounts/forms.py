from django import forms


class InviteStudentsForm(forms.Form):
    student_emails = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}))
