from django import forms
from .models import Year, Department, Degree, Person, Candidate


class RegistrationForm(forms.Form):

    netid = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    middle = forms.CharField(required=False)
    address_street = forms.CharField()
    address_city = forms.CharField()
    address_state = forms.CharField()
    address_zip = forms.CharField()
    email = forms.CharField()
    phone = forms.CharField()
    year = forms.ModelChoiceField(queryset=Year.objects.all().order_by('year'))
    department = forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'))
    degree = forms.ModelChoiceField(queryset=Degree.objects.all().order_by('name'))

    def handle_registration(self):
        candidate_fields = [u'year', u'department', u'degree'] #fields for candidate table, not person table
        person_data = {}
        for field in self.cleaned_data.keys():
            if field not in candidate_fields:
                person_data[field] = self.cleaned_data[field]
        person = Person.objects.create(**person_data)
        candidate_data = {u'person': person}
        for field in self.cleaned_data.keys():
            if field in candidate_fields and self.cleaned_data[field]:
                candidate_data[field] = self.cleaned_data[field]
        candidate = Candidate.objects.create(**candidate_data)
