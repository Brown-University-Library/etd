import hashlib
import os
import unicodedata
from datetime import date
from django.db import models, IntegrityError
from django.db.models import Q
from django.utils import timezone
from . import email


class DuplicateNetidException(Exception):
    pass

class DuplicateOrcidException(Exception):
    pass

class DuplicateEmailException(Exception):
    pass

class CandidateException(Exception):
    pass

class KeywordException(Exception):
    pass

class CommitteeMemberException(Exception):
    pass

class ThesisException(Exception):
    pass


class Year(models.Model):

    year = models.CharField(max_length=5, unique=True)

    def __unicode__(self):
        return self.year


class Department(models.Model):

    name = models.CharField(max_length=190, unique=True)

    def __unicode__(self):
        return self.name


class Degree(models.Model):

    abbreviation = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=190, unique=True)

    def __unicode__(self):
        return self.abbreviation


class Person(models.Model):

    netid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    orcid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    last_name = models.CharField(max_length=190)
    first_name = models.CharField(max_length=190)
    middle = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=190, null=True, unique=True, blank=True) #need length b/c of unique constraint & mysql issues
    address_street = models.CharField(max_length=190, blank=True)
    address_city = models.CharField(max_length=190, blank=True)
    address_state = models.CharField(max_length=2, blank=True)
    address_zip = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        if self.netid == u'':
            self.netid = None
        if self.orcid == u'':
            self.orcid = None
        if self.email == u'':
            self.email = None
        try:
            super(Person, self).save(*args, **kwargs)
        except IntegrityError as ie:
            if "for key 'netid'" in ie.args[1]:
                raise DuplicateNetidException(ie.args[1])
            elif "for key 'orcid'" in ie.args[1]:
                raise DuplicateOrcidException(ie.args[1])
            elif "email" in ie.args[1]:
                raise DuplicateEmailException(ie.args[1])
            else:
                raise


class GradschoolChecklist(models.Model):

    candidate = models.OneToOneField('Candidate', related_name='gradschool_checklist')
    dissertation_fee = models.DateTimeField(null=True, blank=True)
    bursar_receipt = models.DateTimeField(null=True, blank=True)
    gradschool_exit_survey = models.DateTimeField(null=True, blank=True)
    earned_docs_survey = models.DateTimeField(null=True, blank=True)
    pages_submitted_to_gradschool = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return u'Gradschool Checklist'

    def status(self):
        if self.complete():
            return 'Complete'
        else:
            return 'Incomplete'

    def complete(self):
        if self.dissertation_fee and self.bursar_receipt and self.gradschool_exit_survey\
                and self.earned_docs_survey and self.pages_submitted_to_gradschool:
            return True
        else:
            return False


class Language(models.Model):

    code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.code


class Keyword(models.Model):

    text = models.CharField(max_length=190, unique=True)
    search_text = models.CharField(max_length=190, blank=True)
    authority = models.CharField(max_length=100, blank=True)
    authority_uri = models.CharField(max_length=190, blank=True)
    value_uri = models.CharField(max_length=190, blank=True)

    def __unicode__(self):
        return self.text

    def save(self, *args, **kwargs):
        if (self.text is None) or (len(self.text) == 0):
            raise KeywordException('no empty keywords allowed')
        self.text = Keyword.normalize_text(self.text)
        if len(self.text) > 190:
            raise KeywordException('keyword %s too long' % self.text.encode('utf8'))
        self.search_text = Keyword.get_search_text(self.text)
        super(Keyword, self).save(*args, **kwargs)

    @staticmethod
    def normalize_text(text):
        '''Normalize the unicode text, so that we don't get multiple entries in the db
        that look exactly the same, but are still allowed because the characters are different'''
        return unicodedata.normalize('NFD', text)

    @staticmethod
    def get_search_text(nfd_normalized_text):
        return u''.join([c for c in nfd_normalized_text if unicodedata.category(c) != 'Mn']).lower()

    @staticmethod
    def search(term, order=None):
        #this is search, so we're fine with getting fuzzy results
        #  so search the lower-case, no-accent version as well
        queryset = Keyword.objects.filter(Q(text__icontains=term) | Q(search_text__icontains=term))
        if order:
            queryset = queryset.order_by(order)
        return list(queryset)


class FormatChecklist(models.Model):

    thesis = models.OneToOneField('Thesis', related_name='format_checklist')
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


class Thesis(models.Model):
    '''Represents the actual thesis document that a candidate uploads.
    For the thesis, we track the file name, the checksum, and metadata
    such as title, abstract, keywords, and language. There's also a
    format checklist for each thesis.'''
    STATUS_CHOICES = (
            ('not_submitted', 'Not Submitted'),
            ('pending', 'Awaiting Grad School Review'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        )

    candidate = models.OneToOneField('Candidate')
    document = models.FileField()
    file_name = models.CharField(max_length=190)
    checksum = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    keywords = models.ManyToManyField(Keyword)
    language = models.ForeignKey(Language, null=True, blank=True)
    num_prelim_pages = models.CharField(max_length=10, blank=True)
    num_body_pages = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='not_submitted')
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_accepted = models.DateTimeField(null=True, blank=True)
    date_rejected = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = u'Theses'

    @staticmethod
    def calculate_checksum(thesis_file):
        return hashlib.sha1(thesis_file.read()).hexdigest()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.document:
            if not self.document.name.endswith('pdf'):
                raise ThesisException('must be a pdf file')
            if not self.file_name:
                self.file_name = os.path.basename(self.document.name) #grabbing name from tmp file, since we haven't saved yet
            if not self.checksum:
                self.checksum = Thesis.calculate_checksum(self.document)
        super(Thesis, self).save(*args, **kwargs)
        if not hasattr(self, 'format_checklist'):
            self.format_checklist = FormatChecklist.objects.create(thesis=self)

    def update_thesis_file(self, thesis_file):
        self.document = thesis_file
        self.file_name = thesis_file.name
        self.checksum = Thesis.calculate_checksum(self.document)
        self.save()

    def metadata_complete(self):
        if self.title and self.abstract and self.keywords:
            return True
        else:
            return False

    def ready_to_submit(self):
        return (self.document and self.metadata_complete and self.status in ['not_submitted', 'rejected'])

    def submit(self):
        if not self.document:
            raise ThesisException('can\'t submit thesis: no document has been uploaded')
        if not self.metadata_complete():
            raise ThesisException('can\'t submit thesis: metadata incomplete')
        self.status = 'pending'
        self.date_submitted = timezone.now()
        self.save()

    def accept(self):
        if self.status != 'pending':
            raise ThesisException('can only accept theses with a "pending" status')
        self.status = 'accepted'
        self.save()
        email.send_accept_email(self.candidate)

    def reject(self):
        if self.status != 'pending':
            raise ThesisException('can only reject theses with a "pending" status')
        self.status = 'rejected'
        self.save()
        email.send_reject_email(self.candidate)


class CommitteeMember(models.Model):
    MEMBER_ROLES = (
            (u'reader', u'Reader'),
            (u'advisor', u'Advisor'),
        )

    person = models.ForeignKey(Person)
    role = models.CharField(max_length=25, choices=MEMBER_ROLES, default=u'reader')
    department = models.ForeignKey(Department, null=True, blank=True)
    affiliation = models.CharField(max_length=190, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.person, self.role)

    def save(self, *args, **kwargs):
        if not self.department and not self.affiliation:
            raise CommitteeMemberException('either department or affiliation are required')
        super(CommitteeMember, self).save(*args, **kwargs)


class Candidate(models.Model):
    '''Represents a candidate for a degree. Each candidate has a degree that they're
    pursuing, a department that will grant the degree, and a year they're graduating.
    Optionally, a candidate can choose to embargo their thesis for two years.'''

    person = models.ForeignKey(Person)
    date_registered = models.DateField(default=date.today)
    year = models.ForeignKey(Year)
    department = models.ForeignKey(Department)
    degree = models.ForeignKey(Degree)
    embargo_end_year = models.CharField(max_length=4, null=True, blank=True)
    committee_members = models.ManyToManyField(CommitteeMember)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s (%s)' % (self.person, self.year)

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
    def get_candidates_by_status(status, order_by=None):
        if order_by:
            order_by_field = order_by
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
