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
        post_data = request.POST.copy()
        post_data[u'netid'] = request.user.username
        form = RegistrationForm(post_data)
        if form.is_valid():
            form.handle_registration()
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    return render(request, 'etd_app/register.html', {'form': form})
