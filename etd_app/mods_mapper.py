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
