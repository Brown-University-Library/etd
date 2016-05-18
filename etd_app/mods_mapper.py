from __future__ import unicode_literals
from bdrxml import mods


class ModsMapper(object):

    def __init__(self, thesis):
        self.thesis = thesis

    def get_mods(self):
        return self._map_to_mods()

    def _map_to_mods(self):
        mods_obj = mods.make_mods()
        mods_obj.title = self.thesis.title
        mods_obj = self._add_creator(mods_obj)
        mods_obj = self._add_committee(mods_obj)
        mods_obj = self._add_department(mods_obj)
        mods_obj.create_origin_info()
        mods_obj.origin_info.copyright.append(mods.CopyrightDate(date=self.thesis.candidate.year))
        mods_obj.create_physical_description()
        mods_obj.physical_description.extent = '%s, %s p.' % (self.thesis.num_prelim_pages, self.thesis.num_body_pages)
        mods_obj.physical_description.digital_origin = 'born digital'
        mods_obj.notes.append(mods.Note(text='Thesis (%s -- Brown University %s)' % (self.thesis.candidate.degree.abbreviation, self.thesis.candidate.year)))
        mods_obj.resource_type = 'text'
        mods_obj.genres.append(mods.Genre(text='theses', authority='aat'))
        mods_obj.create_abstract()
        mods_obj.abstract.text = self.thesis.abstract
        mods_obj = self._add_keywords(mods_obj)
        return mods_obj

    def _add_creator(self, mods_obj):
        n = mods.Name(type='personal')
        name_text = self._get_name_text(self.thesis.candidate.person)
        np = mods.NamePart(text=name_text)
        n.name_parts.append(np)
        r = mods.Role(type='text', text='creator')
        n.roles.append(r)
        mods_obj.names.append(n)
        return mods_obj

    def _get_name_text(self, person):
        name_text = person.last_name
        if person.first_name:
            name_text += ', %s %s' % (person.first_name, person.middle)
        return name_text.strip()

    def _add_committee(self, mods_obj):
        for cm in self.thesis.candidate.committee_members.all():
            n = mods.Name(type='personal')
            name_text = self._get_name_text(cm.person)
            np = mods.NamePart(text=name_text)
            n.name_parts.append(np)
            r = mods.Role(type='text', text=cm.get_role_display())
            n.roles.append(r)
            mods_obj.names.append(n)
        return mods_obj

    def _add_department(self, mods_obj):
        n = mods.Name(type='corporate')
        name_text = 'Brown University. %s' % self.thesis.candidate.department.name
        np = mods.NamePart(text=name_text)
        n.name_parts.append(np)
        r = mods.Role(type='text', text='sponsor')
        n.roles.append(r)
        mods_obj.names.append(n)
        return mods_obj

    def _add_keywords(self, mods_obj):
        for kw in self.thesis.keywords.all():
            subject = mods.Subject(topic=kw.text)
            if kw.authority:
                subject.authority = kw.authority
            if kw.authority_uri:
                subject.authority_uri = kw.authority_uri
            if kw.value_uri:
                subject.value_uri = kw.value_uri
            mods_obj.subjects.append(subject)
        return mods_obj
