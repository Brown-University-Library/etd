import hashlib
import os
import unicodedata
from datetime import date
from django.db import models


class CandidateCreateException(Exception):
    pass

class KeywordException(Exception):
    pass


class Year(models.Model):

    year = models.CharField(max_length=5, unique=True)


class Department(models.Model):

    name = models.CharField(max_length=190, unique=True)


class Degree(models.Model):

    abbreviation = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=190, unique=True)


class Person(models.Model):

    netid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    orcid = models.CharField(max_length=100, null=True, unique=True, blank=True)
    last_name = models.CharField(max_length=190)
    first_name = models.CharField(max_length=190)
    middle = models.CharField(max_length=100)
    email = models.EmailField()
    address_street = models.CharField(max_length=190)
    address_city = models.CharField(max_length=190)
    address_state = models.CharField(max_length=2)
    address_zip = models.CharField(max_length=20)
    phone = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if self.netid == u'':
            self.netid = None
        if self.orcid == u'':
            self.orcid = None
        super(Person, self).save(*args, **kwargs)


class Candidate(models.Model):

    person = models.ForeignKey(Person)
    date_registered = models.DateField(default=date.today)
    year = models.ForeignKey(Year)
    department = models.ForeignKey(Department)
    degree = models.ForeignKey(Degree)

    def save(self, *args, **kwargs):
        if not self.person.netid:
            raise CandidateCreateException('candidate must have a Brown netid')
        super(Candidate, self).save(*args, **kwargs)


class CommitteeMember(models.Model):
    MEMBER_ROLES = (
            (u'reader', u'Reader'),
            (u'director', u'Director'),
        )

    person = models.ForeignKey(Person)
    role = models.CharField(max_length=25, choices=MEMBER_ROLES, default=u'reader')
    department = models.ForeignKey(Department, null=True, blank=True)
    affiliation = models.CharField(max_length=190)


class Language(models.Model):

    code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)


class Keyword(models.Model):

    text = models.CharField(max_length=190, unique=True)
    search_text = models.CharField(max_length=190, blank=True)
    authority = models.CharField(max_length=100, blank=True)
    authority_uri = models.CharField(max_length=190, blank=True)
    value_uri = models.CharField(max_length=190, blank=True)

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


class Thesis(models.Model):

    candidate = models.ForeignKey(Candidate)
    document = models.FileField()
    file_name = models.CharField(max_length=190)
    checksum = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    abstract = models.TextField()
    keywords = models.ManyToManyField(Keyword)
    language = models.ForeignKey(Language, null=True)
    status = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if self.document:
            if not self.document.name.endswith('pdf'):
                raise Exception('must be a pdf file')
            if not self.file_name:
                self.file_name = os.path.basename(self.document.name) #grabbing name from tmp file, since we haven't saved yet
            if not self.checksum:
                self.checksum = hashlib.sha1(self.document.read()).hexdigest()
        super(Thesis, self).save(*args, **kwargs)
