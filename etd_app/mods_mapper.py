from __future__ import unicode_literals
from bdrxml import mods


class ModsMapper(object):

    def __init__(self, thesis):
        self.thesis = thesis

    def get_mods(self):
        return self._map_to_mods(self.thesis)

    def _map_to_mods(self, thesis):
        mods_obj = mods.make_mods()
        mods_obj.title = thesis.title
        mods_obj = self._add_creator(thesis, mods_obj)
        mods_obj = self._add_committee(thesis, mods_obj)
        mods_obj = self._add_department(thesis, mods_obj)
        mods_obj.create_origin_info()
        mods_obj.origin_info.copyright.append(mods.CopyrightDate(date=thesis.candidate.year))
        mods_obj.create_physical_description()
        mods_obj.physical_description.extent = '%s, %s p.' % (thesis.num_prelim_pages, thesis.num_body_pages)
        mods_obj.physical_description.digital_origin = 'born digital'
        mods_obj.notes.append(mods.Note(text='Thesis (%s -- Brown University %s)' % (thesis.candidate.degree.abbreviation, thesis.candidate.year)))
        mods_obj.resource_type = 'text'
        mods_obj.genres.append(mods.Genre(text='theses', authority='aat'))
        mods_obj.create_abstract()
        mods_obj.abstract.text = thesis.abstract
        mods_obj = self._add_keywords(thesis, mods_obj)
        return mods_obj

    def _add_creator(self, thesis, mods_obj):
        n = mods.Name(type='personal')
        name_text = self._get_name_text(thesis.candidate.person)
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

    def _add_committee(self, thesis, mods_obj):
        for cm in thesis.candidate.committee_members.all():
            n = mods.Name(type='personal')
            name_text = self._get_name_text(cm.person)
            np = mods.NamePart(text=name_text)
            n.name_parts.append(np)
            r = mods.Role(type='text', text=cm.get_role_display())
            n.roles.append(r)
            mods_obj.names.append(n)
        return mods_obj

    def _add_department(self, thesis, mods_obj):
        n = mods.Name(type='corporate')
        name_text = 'Brown University. %s' % thesis.candidate.department.name
        np = mods.NamePart(text=name_text)
        n.name_parts.append(np)
        r = mods.Role(type='text', text='sponsor')
        n.roles.append(r)
        mods_obj.names.append(n)
        return mods_obj

    def _add_keywords(self, thesis, mods_obj):
        for kw in thesis.keywords.all():
            subject = mods.Subject(topic=kw.text)
            if kw.authority:
                subject.authority = kw.authority
            if kw.authority_uri:
                subject.authority_uri = kw.authority_uri
            if kw.value_uri:
                subject.value_uri = kw.value_uri
            mods_obj.subjects.append(subject)
        return mods_obj
