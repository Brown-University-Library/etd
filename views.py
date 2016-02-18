from django.shortcuts import render


def home(request):
    return render(request, 'etd_app/home.html')
