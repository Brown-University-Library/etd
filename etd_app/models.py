import hashlib
import os
import unicodedata
from datetime import date
from django.db import models, IntegrityError
from django.db.models import Q
from django.utils import timezone
from model_utils import Choices
from . import email


STRINGS_TO_REMOVE = ['<br />', '<br>', '<BR>', '\x0b', '\x0c', '\x0e', '\x0f']


def cleanup_user_text(text):
    for bad_text in STRINGS_TO_REMOVE:
        text = text.replace(bad_text, '')
    return text


def normalize_text(text):
    '''Normalizes unicode text, so that we don't get multiple entries in the db
    that look exactly the same, but are still allowed because the characters are different'''
    return unicodedata.normalize('NFD', text)


class DuplicateNetidException(Exception):
    pass

class DuplicateOrcidException(Exception):
    pass

class DuplicateEmailException(Exception):
    pass

class DuplicateBannerIdException(Exception):
    pass

class CandidateException(Exception):
    pass

class KeywordException(Exception):
    pass

class CommitteeMemberException(Exception):
    pass

class ThesisException(Exception):
    pass


class Department(models.Model):

    name = models.CharField(max_length=190, unique=True)
    bdr_collection_id = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def short_name(self):
        return self.name.replace('Department of ', '')


class Degree(models.Model):

    TYPES = Choices(
                ('doctorate', 'Doctorate'),
                ('masters', 'Masters'),
            )

    abbreviation = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=190, unique=True)
    degree_type = models.CharField(max_length=20, choices=TYPES, default=TYPES.doctorate)

    def __str__(self):
        return self.abbreviation

    @property
    def degree_type_adjective(self):
        if self.degree_type == Degree.TYPES.doctorate:
            return 'doctoral'
        else:
            return 'masters'


class Person(models.Model):

    netid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    orcid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    bannerid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    last_name = models.CharField(max_length=190)
    first_name = models.CharField(max_length=190)
    middle = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=190, null=True, unique=True, blank=True) #need length b/c of unique constraint & mysql issues
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def _check_for_duplicate_exception(self, msg):
        if 'duplicate' in msg or 'unique' in msg:
            if 'netid' in msg:
                raise DuplicateNetidException(msg)
            elif 'orcid' in msg:
                raise DuplicateOrcidException(msg)
            elif 'email' in msg:
                raise DuplicateEmailException(msg)
            elif 'bannerid' in msg:
                raise DuplicateBannerIdException(msg)

    def save(self, *args, **kwargs):
        if self.netid == '':
            self.netid = None
        if self.orcid == '':
            self.orcid = None
        if self.email == '':
            self.email = None
        if self.bannerid == '':
            self.bannerid = None
        try:
            super(Person, self).save(*args, **kwargs)
        except IntegrityError as ie:
            if len(ie.args) == 2:
                msg = ie.args[1].lower()
            else:
                msg = ie.args[0].lower()
            #check for duplicate exception to raise
            self._check_for_duplicate_exception(msg)
            #... or just re-raise current exception if it didn't match
            raise

    def get_formatted_name(self):
        name = self.last_name
        if self.first_name:
            name += ', %s %s' % (self.first_name, self.middle)
        return name.strip()


class GradschoolChecklist(models.Model):

    candidate = models.OneToOneField('Candidate', related_name='gradschool_checklist', on_delete=models.PROTECT)
    dissertation_fee = models.DateTimeField(null=True, blank=True)
    bursar_receipt = models.DateTimeField(null=True, blank=True)
    gradschool_exit_survey = models.DateTimeField(null=True, blank=True)
    earned_docs_survey = models.DateTimeField(null=True, blank=True)
    pages_submitted_to_gradschool = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return 'Gradschool Checklist for %s' % self.candidate

    def status(self):
        if self.complete():
            return 'Complete'
        else:
            return 'Incomplete'

    def complete(self):
        if self.bursar_receipt and self.pages_submitted_to_gradschool:
            if self.candidate.degree.degree_type == Degree.TYPES.masters:
                return True
            if self.gradschool_exit_survey and self.earned_docs_survey:
                return True
        return False

    def get_items(self):
        items = [{'display': 'Submit Bursar\'s Office receipt (white) showing that all outstanding debts have been paid', 'completed': self.bursar_receipt, 'staff_label': 'Bursar Receipt', 'form_field_name': 'bursar_receipt'}]
        if self.candidate.degree.degree_type == Degree.TYPES.doctorate:
            items.extend([
                {'display': 'Submit title page, abstract, and signature pages to Graduate School', 'completed': self.pages_submitted_to_gradschool, 'staff_label': 'Signature Page', 'form_field_name': 'pages_submitted_to_gradschool'},
                {'display': 'Complete Graduate School Exit Survey', 'completed': self.gradschool_exit_survey, 'staff_label': 'Grad School Exit Survey', 'form_field_name': 'gradschool_exit_survey'},
                {'display': 'Submit Survey of Earned Doctorates', 'completed': self.earned_docs_survey, 'staff_label': 'Earned Doctorates Survey', 'form_field_name': 'earned_docs_survey'},
               ])
        else:
            items.extend([
                {'display': 'Submit title page and signature pages to Graduate School', 'completed': self.pages_submitted_to_gradschool, 'staff_label': 'Signature Page', 'form_field_name': 'pages_submitted_to_gradschool'},
                ])
        return items


class Language(models.Model):

    code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Keyword(models.Model):

    text = models.CharField(max_length=190, unique=True)
    search_text = models.CharField(max_length=190, blank=True)
    authority = models.CharField(max_length=100, blank=True)
    authority_uri = models.CharField(max_length=190, blank=True)
    value_uri = models.CharField(max_length=190, blank=True)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if (self.text is None) or (len(self.text) == 0):
            raise KeywordException('no empty keywords allowed')
        self.text = cleanup_user_text(self.text)
        self.text = normalize_text(self.text)
        if len(self.text) > 190:
            raise KeywordException('keyword %s too long' % self.text.encode('utf8'))
        self.search_text = Keyword.get_search_text(self.text)
        super(Keyword, self).save(*args, **kwargs)

    @staticmethod
    def get_search_text(nfd_normalized_text):
        return ''.join([c for c in nfd_normalized_text if unicodedata.category(c) != 'Mn']).lower()

    @staticmethod
    def search(term, order=None):
        term = normalize_text(term)
        #this is search, so we're fine with getting fuzzy results
        #  so search the lower-case, no-accent version as well
        queryset = Keyword.objects.filter(Q(text__icontains=term) | Q(search_text__icontains=term))
        if order:
            queryset = queryset.order_by(order)
        return list(queryset)


class FormatChecklist(models.Model):

    thesis = models.OneToOneField('Thesis', related_name='format_checklist', on_delete=models.PROTECT)
    title_page_issue = models.BooleanField(default=False, blank=True)
    title_page_comment = models.CharField(max_length=190, blank=True)
    signature_page_issue = models.BooleanField(default=False, blank=True)
    signature_page_comment = models.CharField(max_length=190, blank=True)
    font_issue = models.BooleanField(default=False, blank=True)
    font_comment = models.CharField(max_length=190, blank=True)
    spacing_issue = models.BooleanField(default=False, blank=True)
    spacing_comment = models.CharField(max_length=190, blank=True)
    margins_issue = models.BooleanField(default=False, blank=True)
    margins_comment = models.CharField(max_length=190, blank=True)
    pagination_issue = models.BooleanField(default=False, blank=True)
    pagination_comment = models.CharField(max_length=190, blank=True)
    format_issue = models.BooleanField(default=False, blank=True)
    format_comment = models.CharField(max_length=190, blank=True)
    graphs_issue = models.BooleanField(default=False, blank=True)
    graphs_comment = models.CharField(max_length=190, blank=True)
    dating_issue = models.BooleanField(default=False, blank=True)
    dating_comment = models.CharField(max_length=190, blank=True)
    general_comments = models.TextField(blank=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'FormatChecklist for %s' % self.thesis.candidate


class Thesis(models.Model):
    '''Represents the actual thesis document that a candidate uploads.
    For the thesis, we track the file name, the checksum, and metadata
    such as title, abstract, keywords, and language. There's also a
    format checklist for each thesis.'''
    STATUS_CHOICES = Choices(
            ('not_submitted', 'Not Submitted'),
            ('pending', 'Awaiting Grad School Review'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('ingested', 'Ingested'),
            ('ingest_error', 'Ingestion Error'),
        )

    candidate = models.OneToOneField('Candidate', on_delete=models.PROTECT)
    document = models.FileField()
    original_file_name = models.CharField(max_length=190)
    checksum = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    keywords = models.ManyToManyField(Keyword)
    language = models.ForeignKey(Language, null=True, blank=True, on_delete=models.PROTECT)
    num_prelim_pages = models.CharField(max_length=10, blank=True)
    num_body_pages = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_CHOICES.not_submitted)
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_accepted = models.DateTimeField(null=True, blank=True)
    date_rejected = models.DateTimeField(null=True, blank=True)
    pid = models.CharField(max_length=50, null=True, unique=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Theses'

    @staticmethod
    def calculate_checksum(thesis_file):
        return hashlib.sha1(thesis_file.read()).hexdigest()

    def __str__(self):
        return self.title

    def _get_default_language(self):
        try:
            lang = Language.objects.get(name='English')
        except Language.DoesNotExist:
            lang = Language.objects.create(code='eng', name='English')
        return lang

    def save(self, *args, **kwargs):
        if self.pid == '':
            self.pid = None
        if self.document:
            if not self.document.name.endswith('pdf'):
                raise ThesisException('must be a pdf file')
            if not self.original_file_name:
                self.original_file_name = os.path.basename(self.document.name) #grabbing name from tmp file, since we haven't saved yet
            if not self.checksum:
                self.checksum = Thesis.calculate_checksum(self.document)
        if not self.language:
            self.language = self._get_default_language()
        if self.abstract:
            self.abstract = cleanup_user_text(self.abstract)
        if self.title:
            self.title = cleanup_user_text(self.title)
        super(Thesis, self).save(*args, **kwargs)
        if not hasattr(self, 'format_checklist'):
            self.format_checklist = FormatChecklist.objects.create(thesis=self)

    @property
    def full_label(self):
        if self.candidate.degree.degree_type == Degree.TYPES.masters:
            return 'Masters Thesis'
        else:
            return 'PhD Dissertation'

    @property
    def label(self):
        if self.candidate.degree.degree_type == Degree.TYPES.masters:
            return 'Thesis'
        else:
            return 'Dissertation'

    @property
    def current_file_name(self):
        return os.path.basename(self.document.name)

    def update_thesis_file(self, thesis_file):
        self.document = thesis_file
        self.original_file_name = thesis_file.name
        self.checksum = Thesis.calculate_checksum(self.document)
        self.save()

    def metadata_complete(self):
        if self.title and self.abstract and self.keywords:
            return True
        else:
            return False

    def ready_to_submit(self):
        return bool(self.document and self.metadata_complete() and
                (self.status in [Thesis.STATUS_CHOICES.not_submitted, Thesis.STATUS_CHOICES.rejected]) and
                self.candidate.committee_members.exists())

    def submit(self):
        if not self.document:
            raise ThesisException('can\'t submit thesis: no document has been uploaded')
        if not self.metadata_complete():
            raise ThesisException('can\'t submit thesis: metadata incomplete')
        if not self.status in ['not_submitted', 'rejected']:
            raise ThesisException('can\'t submit thesis: wrong status of %s' % self.status)
        if not self.candidate.committee_members.exists():
            raise ThesisException('can\'t submit thesis: no committee members')
        self.status = 'pending'
        self.date_submitted = timezone.now()
        self.save()
        email.send_submit_email_to_gradschool(self.candidate)

    def accept(self):
        if self.status != 'pending':
            raise ThesisException('can only accept theses with a "pending" status')
        self.status = 'accepted'
        self.save()
        email.send_accept_email(self.candidate)

    def is_locked(self):
        #this means the student can't edit anything on the dissertation anymore
        return (self.status not in [Thesis.STATUS_CHOICES.not_submitted, Thesis.STATUS_CHOICES.rejected])

    def reject(self):
        if self.status != 'pending':
            raise ThesisException('can only reject theses with a "pending" status')
        self.status = Thesis.STATUS_CHOICES.rejected
        self.save()
        email.send_reject_email(self.candidate)

    def ready_to_ingest(self):
        current_year = date.today().year
        if self.status == Thesis.STATUS_CHOICES.accepted:
            if self.candidate.gradschool_checklist.complete():
                if self.candidate.year <= current_year:
                    return True
        return False

    def mark_ingested(self, pid):
        self.pid = pid
        self.status = Thesis.STATUS_CHOICES.ingested
        self.save()

    def mark_ingest_error(self):
        self.status = Thesis.STATUS_CHOICES.ingest_error
        self.save()

    def open_for_reupload(self):
        if self.status not in [Thesis.STATUS_CHOICES.pending, Thesis.STATUS_CHOICES.accepted]:
            raise ThesisException('can only open a thesis for re-upload if it\'s "Awaiting Gradschool Review" or "Accepted"')
        self.status = Thesis.STATUS_CHOICES.not_submitted
        self.save()


class CommitteeMember(models.Model):
    MEMBER_ROLES = Choices(
            ('reader', 'Reader'),
            ('advisor', 'Advisor'),
        )

    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    role = models.CharField(max_length=25, choices=MEMBER_ROLES, default=MEMBER_ROLES.reader)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, help_text='Enter either Brown department OR external affiliation.')
    affiliation = models.CharField(max_length=190, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s (%s)' % (self.person, self.role)

    def save(self, *args, **kwargs):
        if not self.department and not self.affiliation:
            raise CommitteeMemberException('either department or affiliation are required')
        super(CommitteeMember, self).save(*args, **kwargs)


class Candidate(models.Model):
    '''Represents a candidate for a degree. Each candidate has a degree that they're
    pursuing, a department that will grant the degree, and a year they're graduating.
    Optionally, a candidate can choose to embargo their thesis for two years.'''

    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    date_registered = models.DateField(default=date.today)
    year = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    degree = models.ForeignKey(Degree, on_delete=models.PROTECT)
    embargo_end_year = models.IntegerField(null=True, blank=True)
    private_access_end_date = models.DateField(null=True, blank=True)
    committee_members = models.ManyToManyField(CommitteeMember)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.person} ({self.degree} - {self.year})'

    def save(self, *args, **kwargs):
        if not self.person.netid:
            raise CandidateException('candidate must have a Brown netid')
        if not self.person.email:
            raise CandidateException('candidate must have an email')
        super(Candidate, self).save(*args, **kwargs)
        if not hasattr(self, 'gradschool_checklist'):
            GradschoolChecklist.objects.create(candidate=self)
        if not hasattr(self, 'thesis'):
            Thesis.objects.create(candidate=self)

    @staticmethod
    def _get_order_by_field(sort_by_param):
        if sort_by_param == 'title':
            return 'thesis__title'
        elif sort_by_param == 'date_registered':
            return 'date_registered'
        elif sort_by_param == 'date_submitted':
            return 'thesis__date_submitted'
        elif sort_by_param == 'department':
            return 'department__name'
        elif sort_by_param == 'status':
            return 'thesis__status'
        else:
            return 'person__last_name'

    @staticmethod
    def get_candidates_by_status(status, sort_param=None):
        if sort_param:
            order_by_field = Candidate._get_order_by_field(sort_param)
        else:
            order_by_field = 'person__last_name'
        if status == 'all':
            return Candidate.objects.all().order_by(order_by_field)
        elif status == 'in_progress': #dissertation not submitted yet
            return Candidate.objects.filter(thesis__status='not_submitted').order_by(order_by_field)
        elif status == 'awaiting_gradschool': #dissertation submitted, needs to be checked by grad school
            return Candidate.objects.filter(thesis__status='pending').order_by(order_by_field)
        elif status == 'dissertation_rejected': #dissertation needs to be resubmitted
            return Candidate.objects.filter(thesis__status='rejected').order_by(order_by_field)
        elif status == 'paperwork_incomplete': #dissertation approved, still need paperwork
            return [c for c in Candidate.objects.filter(thesis__status='accepted').order_by(order_by_field) if not c.gradschool_checklist.complete()]
        elif status == 'complete': #dissertation approved, paperwork complete - everything done
            return [c for c in Candidate.objects.filter(thesis__status='accepted').order_by(order_by_field) if c.gradschool_checklist.complete()]
