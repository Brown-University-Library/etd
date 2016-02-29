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
