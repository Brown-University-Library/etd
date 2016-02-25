from django import forms
from .models import Year, Department, Degree, Person, Candidate, Thesis


class RegistrationForm(forms.Form):

    CANDIDATE_FIELDS = [u'year', u'department', u'degree'] #fields for candidate table, not person table

    netid = forms.CharField(widget=forms.HiddenInput())
    first_name = forms.CharField(label=u'First Name')
    last_name = forms.CharField(label=u'Last Name')
    middle = forms.CharField(required=False)
    address_street = forms.CharField(label=u'Street')
    address_city = forms.CharField(label=u'City')
    address_state = forms.CharField(label=u'State')
    address_zip = forms.CharField(label=u'Zip')
    email = forms.CharField()
    phone = forms.CharField()
    year = forms.ModelChoiceField(queryset=Year.objects.all().order_by('year'))
    department = forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'))
    degree = forms.ModelChoiceField(queryset=Degree.objects.all().order_by('name'))

    def _create_person(self, cleaned_data):
        person_data = {}
        for field in self.cleaned_data.keys():
            if field not in RegistrationForm.CANDIDATE_FIELDS:
                person_data[field] = self.cleaned_data[field]
        person = Person.objects.create(**person_data)
        return person

    def _create_candidate(self, cleaned_data, person):
        candidate_data = {u'person': person}
        for field in self.cleaned_data.keys():
            if field in RegistrationForm.CANDIDATE_FIELDS and self.cleaned_data[field]:
                candidate_data[field] = self.cleaned_data[field]
        Candidate.objects.create(**candidate_data)

    def handle_registration(self):
        person = self._create_person(self.cleaned_data)
        self._create_candidate(self.cleaned_data, person)


class UploadForm(forms.Form):

    thesis_file = forms.FileField()

    def save_upload(self, candidate):
        Thesis.objects.create(candidate=candidate, document=self.cleaned_data['thesis_file'])
