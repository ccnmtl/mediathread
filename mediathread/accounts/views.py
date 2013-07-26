from django.views.generic.edit import FormView
from django.shortcuts import render
from .forms import RegistrationForm
def invite_students(request):
    pass

def registration_form(request):
    if request.method == 'POST':
        pass
        #redirect to result page
    else:
        form = RegistrationForm()

    return render(request, 'account/registration_form.html', {
        'form': form
        })

