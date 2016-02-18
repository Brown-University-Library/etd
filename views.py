from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    return render(request, 'etd_app/home.html')


def overview(request):
    return render(request, 'etd_app/overview.html')


def faq(request):
    return render(request, 'etd_app/faq.html')


def tutorials(request):
    return render(request, 'etd_app/tutorials.html')


def copyright(request):
    return render(request, 'etd_app/copyright.html')


@login_required
def register(request):
    from .forms import RegistrationForm
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
    else:
        form = RegistrationForm()
    return render(request, 'etd_app/register.html', {'form': form})
