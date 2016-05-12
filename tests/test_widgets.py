# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import QueryDict
from django.test import TestCase
from etd_app.models import Keyword
from etd_app.widgets import KeywordSelect2TagWidget, ID_VAL_SEPARATOR, FAST_URI
from .test_models import COMPOSED_TEXT, DECOMPOSED_TEXT


class TestKeywordTagWidget(TestCase):

    def test_empty_keyword(self):
        data = QueryDict('keywords=')
        files = {}
        field_name = 'keywords'
        widget = KeywordSelect2TagWidget()
        value_from_datadict = widget.value_from_datadict(data, files, field_name)
        self.assertEqual(value_from_datadict, [])

    def test_existing_keyword(self):
        k = Keyword.objects.create(text='test')
        data = QueryDict('keywords=%s' % k.id)
        files = {}
        field_name = 'keywords'
        widget = KeywordSelect2TagWidget()
        value_from_datadict = widget.value_from_datadict(data, files, field_name)
        self.assertEqual(value_from_datadict, [str(k.id)])

    def test_new_keyword(self):
        data = QueryDict('keywords=dogs')
        files = {}
        field_name = 'keywords'
        widget = KeywordSelect2TagWidget()
        value_from_datadict = widget.value_from_datadict(data, files, field_name)
        self.assertEqual(Keyword.objects.all()[0].id, int(value_from_datadict[0]))

    def test_user_enters_composed_text(self):
        k = Keyword.objects.create(text=COMPOSED_TEXT)
        self.assertEqual(k.text, DECOMPOSED_TEXT)
        data_text = 'keywords=%s' % COMPOSED_TEXT
        data = QueryDict(data_text.encode('utf8'))
        files = {}
        field_name = 'keywords'
        widget = KeywordSelect2TagWidget()
        value_from_datadict = widget.value_from_datadict(data, files, field_name)
        self.assertEqual(Keyword.objects.all()[0].id, int(value_from_datadict[0]))

    def test_fast_keyword(self):
        kw_text = Keyword.normalize_text('Lîon')
        post_string = 'keywords=fst123456%s%s' % (ID_VAL_SEPARATOR, kw_text)
        data = QueryDict(post_string.encode('utf8'))
        files = {}
        field_name = 'keywords'
        widget = KeywordSelect2TagWidget()
        value_from_datadict = widget.value_from_datadict(data, files, field_name)
        new_keyword = Keyword.objects.all()[0]
        self.assertEqual(new_keyword.text, kw_text)
        self.assertEqual(new_keyword.authority, 'fast')
        self.assertEqual(new_keyword.authority_uri, FAST_URI)
        self.assertEqual(new_keyword.value_uri, '%s/123456' % FAST_URI)
