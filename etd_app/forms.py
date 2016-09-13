from __future__ import unicode_literals
from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


from .models import Department, Degree, Person, Candidate, Thesis, FormatChecklist, CommitteeMember
from .widgets import KeywordSelect2TagWidget, ID_VAL_SEPARATOR
from . import email


class PersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ['netid', 'first_name', 'last_name', 'middle', 'orcid', 'email']
        widgets = { 'netid': forms.HiddenInput() }
        labels = {
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'orcid': 'ORCID',
            }
        help_texts = {
                'first_name': 'Must match name on thesis or dissertation',
                'last_name': 'Must match name on thesis or dissertation',
                'orcid': 'Won\'t be published',
                'email': 'Won\'t be published',
            }

    def __init__(self, *args, **kwargs):
        degree_type = kwargs.pop('degree_type', '')
        super(PersonForm, self).__init__(*args, **kwargs)
        if degree_type == 'dissertation':
            self.fields['first_name'].help_text = 'Must match name on dissertation'
            self.fields['last_name'].help_text = 'Must match name on dissertation'
        elif degree_type == 'thesis':
            self.fields['first_name'].help_text = 'Must match name on thesis'
            self.fields['last_name'].help_text = 'Must match name on thesis'
        self.helper = FormHelper()
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_tag=False


class CommitteeMemberPersonForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ['first_name', 'last_name']
        labels = {
                'first_name': 'First Name',
                'last_name': 'Last Name',
            }

    def __init__(self, *args, **kwargs):
        super(CommitteeMemberPersonForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_tag=False


def get_years():
    current_year = datetime.now().year
    return (
            (current_year, current_year),
            (current_year+1, current_year+1),
            )


class CandidateForm(forms.ModelForm):

    year = forms.ChoiceField(choices=get_years)
    department = forms.ModelChoiceField(queryset=Department.objects.all().order_by('name'),
            help_text='If your department is missing, please email bdr@brown.edu and we\'ll add it to the list.')
    set_embargo = forms.BooleanField(required=False)

    class Meta:
        model = Candidate
        fields = ['year', 'department', 'degree', 'embargo_end_year']
        widgets = {'embargo_end_year': forms.HiddenInput()}

    def clean(self):
        super(CandidateForm, self).clean()
        if self.cleaned_data['set_embargo'] and not self.errors:
            self.cleaned_data['embargo_end_year'] = str(int(self.cleaned_data['year']) + 2)
        del self.cleaned_data['set_embargo']

    def __init__(self, *args, **kwargs):
        degree_type = kwargs.pop('degree_type', '')
        super(CandidateForm, self).__init__(*args, **kwargs)
        degrees = Degree.objects.all().order_by('name')
        embargo_label = 'Restrict access to my %s for 2 years (see <a href="https://www.brown.edu/academics/gradschool/dissertation-guidelines">Guidelines</a>)'
        self.fields['set_embargo'].label = embargo_label % 'dissertation'
        if degree_type == 'dissertation':
            degrees = degrees.filter(degree_type=Degree.TYPES.doctorate)
        elif degree_type == 'thesis':
            degrees = degrees.filter(degree_type=Degree.TYPES.masters)
            self.fields['set_embargo'].label = embargo_label % 'thesis'
        self.fields['degree'] = forms.ModelChoiceField(queryset=degrees, empty_label=None,
                            widget=forms.RadioSelect(choices=degrees))
        if len(degrees) == 1:
            self.fields['degree'].initial = degrees[0]
        self.helper = FormHelper()
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.form_tag=False
        self.helper.add_input(Submit('submit', 'Save Profile'))


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

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Upload File'))


class MetadataForm(forms.ModelForm):

    class Meta:
        model = Thesis
        fields = ['title', 'abstract', 'keywords', 'language', 'num_prelim_pages', 'num_body_pages']
        labels = {
                'keywords': 'Topics',
                'num_prelim_pages': 'No. of preliminary pages (roman numerals, e.g. ix)',
                'num_body_pages': 'No. of pages in dissertation proper (arabic numerals, e.g. 125)',
            }
        widgets = {
                'keywords': KeywordSelect2TagWidget(),
            }
        help_texts = {
                'title': 'Must match the actual title of your dissertation',
                'keywords': '<a target="_blank" href="http://www.oclc.org/research/themes/data-science/fast.html">What are FAST results?</a>',
            }

    def __init__(self, *args, **kwargs):
        super(MetadataForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action="candidate_metadata"
        self.helper.add_input(Submit('submit', 'Save Metadata'))


class GradschoolChecklistForm(forms.Form):

    dissertation_fee = forms.BooleanField(required=False)
    bursar_receipt = forms.BooleanField(required=False)
    gradschool_exit_survey = forms.BooleanField(required=False)
    earned_docs_survey = forms.BooleanField(required=False)
    pages_submitted_to_gradschool = forms.BooleanField(required=False)

    def save_data(self, candidate):
        checklist = candidate.gradschool_checklist
        now = timezone.now()
        email_fields = []
        for field in ['dissertation_fee', 'bursar_receipt', 'gradschool_exit_survey', 'earned_docs_survey', 'pages_submitted_to_gradschool']:
            if self.cleaned_data[field]:
                setattr(checklist, field, now)
                email_fields.append(field)
        checklist.save()
        for field in email_fields:
            email.send_paperwork_email(candidate, field)
        if checklist.complete():
            email.send_complete_email(candidate)


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
            candidate.thesis.accept()
        if 'reject_diss' in post_data:
            candidate.thesis.reject()

    def __init__(self, *args, **kwargs):
        super(FormatChecklistForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('accept_diss', 'Approve'))
        self.helper.add_input(Submit('reject_diss', 'Reject'))
        self.helper.add_input(Submit('save', 'Save for Later'))
        self.helper.form_tag=False

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

    def __init__(self, *args, **kwargs):
        super(CommitteeMemberForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.add_input(Submit('submit', 'Save Committee Member'))
        self.helper.form_tag=False
