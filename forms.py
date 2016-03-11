from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Year, Department, Degree, Person, Candidate, Thesis, FormatChecklist, CommitteeMember
from .widgets import KeywordSelect2TagWidget
from . import email


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ['netid', 'first_name', 'last_name', 'middle', 'orcid', 'address_street',
                  'address_city', 'address_state', 'address_zip', 'email', 'phone']
        widgets = { 'netid': forms.HiddenInput() }
        labels = {
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'address_street': 'Street',
                'address_city': 'City',
                'address_state': 'State',
                'address_zip': 'Zip'
            }


class CommitteeMemberPersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ['first_name', 'last_name']
        labels = {
                'first_name': 'First Name',
                'last_name': 'Last Name',
            }


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
        if candidate.thesis:
            candidate.thesis.update_thesis_file(self.cleaned_data['thesis_file'])
        else:
            thesis = Thesis.objects.create(document=self.cleaned_data['thesis_file'])
            candidate.thesis = thesis
            candidate.save()


class MetadataForm(forms.ModelForm):

    class Meta:
        model = Thesis
        fields = ['title', 'abstract', 'keywords', 'language', 'num_prelim_pages', 'num_body_pages']
        labels = {
                'num_prelim_pages': 'No. of preliminary pages (roman numerals, e.g. ix)',
                'num_body_pages': 'No. of pages in dissertation proper (arabic numerals, e.g. 125)',
            }
        widgets = {
                'keywords': KeywordSelect2TagWidget(data_view='autocomplete_keywords',
                    attrs={'data-token-separators': '["\t"]',
                           'data-ajax--delay': 250}),
            }

    def save_metadata(self, candidate):
        thesis = self.save()
        candidate.thesis = thesis
        candidate.save()


class GradschoolChecklistForm(forms.Form):

    dissertation_fee = forms.BooleanField(required=False)
    bursar_receipt = forms.BooleanField(required=False)
    gradschool_exit_survey = forms.BooleanField(required=False)
    earned_docs_survey = forms.BooleanField(required=False)
    pages_submitted_to_gradschool = forms.BooleanField(required=False)

    def save_data(self, candidate):
        checklist = candidate.gradschool_checklist
        now = timezone.now()
        for field in ['dissertation_fee', 'bursar_receipt', 'gradschool_exit_survey', 'earned_docs_survey', 'pages_submitted_to_gradschool']:
            if self.cleaned_data[field]:
                setattr(checklist, field, now)
                email.send_paperwork_email(candidate, field)
        checklist.save()


class FormatChecklistForm(forms.ModelForm):

    class Meta:
        model = FormatChecklist
        fields = ['title_page_issue', 'title_page_comment',
                  'signature_page_issue', 'signature_page_comment',
                  'font_issue', 'font_comment',
                  'spacing_issue', 'spacing_comment',
                  'margins_issue', 'margins_comment',
                  'pagination_issue', 'pagination_comment',
                  'format_issue', 'format_comment',
                  'graphs_issue', 'graphs_comment',
                  'dating_issue', 'dating_comment',
                  'general_comments']

    def handle_post(self, post_data, candidate):
        self.save()
        if 'accept_diss' in post_data:
            candidate.thesis.accept(candidate)
        if 'reject_diss' in post_data:
            candidate.thesis.reject(candidate)


class CommitteeMemberForm(forms.ModelForm):

    class Meta:
        model = CommitteeMember
        fields = ['role', 'department', 'affiliation']
        labels = {
                'department': 'Brown Department'
            }

    def clean(self):
        super(CommitteeMemberForm, self).clean()
        if not self.cleaned_data['department'] and not self.cleaned_data['affiliation']:
            raise ValidationError('Please enter either a Brown Department or an Affiliation.', code='department_or_affiliation_required')
