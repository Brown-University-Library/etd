from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Candidate


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
            return HttpResponseRedirect(reverse('candidate_home'))
    else:
        form = RegistrationForm()
    return render(request, 'etd_app/register.html', {'form': form})


@login_required
def candidate_home(request):
    netid = request.user.username
    try:
        candidate = Candidate.objects.get(person__netid=netid)
    except Candidate.DoesNotExist:
        return HttpResponseRedirect(reverse('register'))
    return render(request, 'etd_app/candidate.html', {'candidate': candidate})
