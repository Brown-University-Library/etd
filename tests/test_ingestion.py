# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase

from etd_app.mods_mapper import ModsMapper
from tests.test_models import LAST_NAME, FIRST_NAME, add_metadata_to_thesis
from tests.test_views import CandidateCreator


class TestModsMapper(TestCase, CandidateCreator):

    def test_mapping(self):
        self._create_candidate()
        self.candidate.person.middle = 'Middle'
        add_metadata_to_thesis(self.candidate.thesis)
        mapper = ModsMapper(self.candidate.thesis)
        mods = mapper.get_mods()
        self.assertEqual(mods.title, 'test')
        creators = [n for n in mods.names if (n.roles[0].text == 'creator') and (n.roles[0].type == 'text')]
        self.assertEqual(creators[0].name_parts[0].text, '%s, %s Middle' % (LAST_NAME, FIRST_NAME))

    def test_creator_no_middle(self):
        self._create_candidate()
        add_metadata_to_thesis(self.candidate.thesis)
        mapper = ModsMapper(self.candidate.thesis)
        mods = mapper.get_mods()
        creators = [n for n in mods.names if n.roles[0].text == 'creator']
        self.assertEqual(creators[0].name_parts[0].text, '%s, %s' % (LAST_NAME, FIRST_NAME))
