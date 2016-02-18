from django import forms
from .models import Year, Department


class RegistrationForm(forms.Form):

    first_name = forms.CharField()
    last_name = forms.CharField()
    middle = forms.CharField()
    street = forms.CharField()
    city = forms.CharField()
    state = forms.CharField()
    zip_code = forms.CharField()
    email = forms.CharField()
    phone = forms.CharField()
    year = forms.ModelChoiceField(queryset=Year.objects.all().order_by('year'))
    department = forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'))
