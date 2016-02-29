from django import forms
from django.core.exceptions import ValidationError
from .models import Year, Department, Degree, Person, Candidate, Thesis


class PersonForm(forms.ModelForm):

    netid = forms.CharField(widget=forms.HiddenInput())
    first_name = forms.CharField(label=u'First Name')
    last_name = forms.CharField(label=u'Last Name')
    middle = forms.CharField(required=False)
    orcid = forms.CharField(required=False)
    address_street = forms.CharField(label=u'Street')
    address_city = forms.CharField(label=u'City')
    address_state = forms.CharField(label=u'State')
    address_zip = forms.CharField(label=u'Zip')
    email = forms.CharField()
    phone = forms.CharField()

    class Meta:
        model = Person
        fields = ['netid', 'orcid', 'first_name', 'last_name', 'middle', 'address_street',
                  'address_city', 'address_state', 'address_zip', 'email', 'phone']

    def _get_or_create_person(self, cleaned_data):
        '''checks the db for an existing person, matching by netid or orcid,
        since those must be unique. If the person is created here, it's not saved.'''
        if 'netid' in cleaned_data:
            try:
                person = Person.objects.get(netid=cleaned_data['netid'])
            except Person.DoesNotExist:
                try:
                    person = Person.objects.get(orcid=cleaned_data['orcid'])
                except Person.DoesNotExist:
                    person = Person()
        return person

    def _create_person(self, cleaned_data):
        person = self._get_or_create_person(cleaned_data)
        for field in cleaned_data.keys():
            if field not in RegistrationForm.CANDIDATE_FIELDS:
                setattr(person, field, cleaned_data[field])
        person.save()
        return person

    def _create_candidate(self, cleaned_data, person):
        try:
            candidate = Candidate.objects.get(person=person)
        except Candidate.DoesNotExist:
            candidate = Candidate(person=person)
        for field in cleaned_data.keys():
            if field in RegistrationForm.CANDIDATE_FIELDS and cleaned_data[field]:
                setattr(candidate, field, cleaned_data[field])
        candidate.save()

    def handle_registration(self):
        person = self._create_person(self.cleaned_data)
        self._create_candidate(self.cleaned_data, person)


class CandidateForm(forms.ModelForm):

    year = forms.ModelChoiceField(queryset=Year.objects.all().order_by('year'))
    department = forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'))
    degree = forms.ModelChoiceField(queryset=Degree.objects.all().order_by('name'))
    set_embargo = forms.BooleanField(label=u'Restrict access to my dissertation for 2 years.', required=False)

    class Meta:
        model = Candidate
        fields = ['year', 'department', 'degree', 'embargo_end_year']
        widgets = {'embargo_end_year': forms.HiddenInput()}

    def clean(self):
        super(CandidateForm, self).clean()
        if self.cleaned_data['set_embargo']:
            self.cleaned_data['embargo_end_year'] = str(int(self.cleaned_data['year'].year) + 2)
        del self.cleaned_data['set_embargo']


def pdf_validator(field_file):
    if not field_file.name.endswith('.pdf'):
        raise ValidationError('file must be a PDF')


class UploadForm(forms.Form):

    thesis_file = forms.FileField(validators=[pdf_validator])

    def save_upload(self, candidate):
        #there could already be a thesis for this candidate, so check for that first
        existing_theses = Thesis.objects.filter(candidate=candidate)
        if existing_theses:
            thesis = existing_theses[0]
            thesis.update_thesis_file(self.cleaned_data['thesis_file'])
        else:
            Thesis.objects.create(candidate=candidate, document=self.cleaned_data['thesis_file'])

class MetadataForm(forms.ModelForm):

    class Meta:
        model = Thesis
        fields = ['candidate', 'title', 'abstract', 'keywords', 'language']
        widgets = {
                'candidate': forms.HiddenInput(),
            }
