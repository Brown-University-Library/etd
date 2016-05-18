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
        self.mods_obj.names.extend(self._get_creators())
        self.mods_obj.names.extend(self._get_committee_names())
        self.mods_obj.names.extend(self._get_department_names())
        self.mods_obj.create_origin_info()
        self.mods_obj.origin_info.copyright.append(mods.CopyrightDate(date=self.thesis.candidate.year))
        self.mods_obj.create_physical_description()
        self.mods_obj.physical_description.extent = '%s, %s p.' % (self.thesis.num_prelim_pages, self.thesis.num_body_pages)
        self.mods_obj.physical_description.digital_origin = 'born digital'
        self.mods_obj.notes.append(mods.Note(text='Thesis (%s -- Brown University %s)' % (self.thesis.candidate.degree.abbreviation, self.thesis.candidate.year)))
        self.mods_obj.resource_type = 'text'
        self.mods_obj.genres.append(mods.Genre(text='theses', authority='aat'))
        self.mods_obj.create_abstract()
        self.mods_obj.abstract.text = self.thesis.abstract
        self.mods_obj.subjects.extend(self._get_keyword_subjects())

    def _get_creators(self):
        creators = []
        n = mods.Name(type='personal')
        name_text = self._get_name_text(self.thesis.candidate.person)
        np = mods.NamePart(text=name_text)
        n.name_parts.append(np)
        r = mods.Role(type='text', text='creator')
        n.roles.append(r)
        creators.append(n)
        return creators

    def _get_name_text(self, person):
        name_text = person.last_name
        if person.first_name:
            name_text += ', %s %s' % (person.first_name, person.middle)
        return name_text.strip()

    def _get_committee_names(self):
        committee_names = []
        for cm in self.thesis.candidate.committee_members.all():
            n = mods.Name(type='personal')
            name_text = self._get_name_text(cm.person)
            np = mods.NamePart(text=name_text)
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
