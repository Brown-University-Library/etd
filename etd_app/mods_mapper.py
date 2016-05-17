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
        return mods_obj

    def _add_creator(self, thesis, mods_obj):
        n = mods.Name()
        name_text = '%s, %s %s' % (thesis.candidate.person.last_name, thesis.candidate.person.first_name, thesis.candidate.person.middle)
        np = mods.NamePart(text=name_text.strip())
        n.name_parts.append(np)
        r = mods.Role(type='text', text='creator')
        n.roles.append(r)
        mods_obj.names.append(n)
        return mods_obj
