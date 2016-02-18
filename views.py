from django.shortcuts import render


def home(request):
    return render(request, 'etd_app/home.html')


def overview(request):
    return render(request, 'etd_app/overview.html')


def tutorials(request):
    return render(request, 'etd_app/tutorials.html')
