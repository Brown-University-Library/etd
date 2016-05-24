from __future__ import unicode_literals
from bdrxml import mods


class ModsMapper(object):

    def __init__(self, thesis):
        self.thesis = thesis
        self.mods_obj = mods.make_mods()
        self._map_to_mods()

    def get_mods(self):
        return self.mods_obj

    def _map_to_mods(self):
        self.mods_obj.title = self.thesis.title
        self.mods_obj.resource_type = 'text'
        self.mods_obj.names.extend(self._get_creators())
        self.mods_obj.names.extend(self._get_committee_names())
        self.mods_obj.names.extend(self._get_department_names())
        self.mods_obj.create_origin_info()
        self.mods_obj.origin_info.copyright.append(self._get_copyright_date())
        self.mods_obj.create_physical_description()
        self.mods_obj.physical_description.extent = self._get_extent()
        self.mods_obj.physical_description.digital_origin = self._get_digital_origin()
        self.mods_obj.notes.extend(self._get_notes())
        self.mods_obj.genres.extend(self._get_genres())
        self.mods_obj.create_abstract()
        self.mods_obj.abstract.text = self._get_abstract()
        self.mods_obj.subjects.extend(self._get_keyword_subjects())
        self.mods_obj.languages.extend(self._get_languages())

    def _get_languages(self):
        langs = []
        if self.thesis.language:
            lang = mods.Language()
            term = mods.LanguageTerm(text=self.thesis.language.name, authority='iso639-2b')
            lang.terms.append(term)
            langs.append(lang)
        return langs

    def _get_notes(self):
        candidate = self.thesis.candidate
        note_text = 'Thesis (%s -- Brown University %s)' % (candidate.degree.abbreviation, candidate.year)
        return [mods.Note(text=note_text)]

    def _get_abstract(self):
        return self.thesis.abstract

    def _get_copyright_date(self):
        return mods.CopyrightDate(date=self.thesis.candidate.year)

    def _get_extent(self):
        return '%s, %s p.' % (self.thesis.num_prelim_pages, self.thesis.num_body_pages)

    def _get_digital_origin(self):
        return 'born digital'

    def _get_genres(self):
        return [mods.Genre(text='theses', authority='aat')]

    def _get_creators(self):
        creators = []
        n = mods.Name(type='personal')
        np = mods.NamePart(text=self.thesis.candidate.person.get_formatted_name())
        n.name_parts.append(np)
        r = mods.Role(type='text', text='creator')
        n.roles.append(r)
        creators.append(n)
        return creators

    def _get_committee_names(self):
        committee_names = []
        for cm in self.thesis.candidate.committee_members.all():
            n = mods.Name(type='personal')
            np = mods.NamePart(text=cm.person.get_formatted_name())
            n.name_parts.append(np)
            r = mods.Role(type='text', text=cm.get_role_display())
            n.roles.append(r)
            committee_names.append(n)
        return committee_names

    def _get_department_names(self):
        department_names = []
        n = mods.Name(type='corporate')
        name_text = 'Brown University. %s' % self.thesis.candidate.department.name
        np = mods.NamePart(text=name_text)
        n.name_parts.append(np)
        r = mods.Role(type='text', text='sponsor')
        n.roles.append(r)
        department_names.append(n)
        return department_names

    def _get_keyword_subjects(self):
        keywords = []
        for kw in self.thesis.keywords.all():
            subject = mods.Subject(topic=kw.text)
            if kw.authority:
                subject.authority = kw.authority
            if kw.authority_uri:
                subject.authority_uri = kw.authority_uri
            if kw.value_uri:
                subject.value_uri = kw.value_uri
            keywords.append(subject)
        return keywords
