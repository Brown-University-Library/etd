# -*- coding: utf-8 -*-
from django.http import QueryDict
from django.test import TestCase
from .models import Keyword
from .widgets import KeywordSelect2TagWidget
from .test_models import COMPOSED_TEXT, DECOMPOSED_TEXT


class TestKeywordTagWidget(TestCase):

    def test_existing_keyword(self):
        k = Keyword.objects.create(text=u'test')
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
        data = QueryDict('keywords=%s' % COMPOSED_TEXT.encode('utf8'))
        files = {}
        field_name = 'keywords'
        widget = KeywordSelect2TagWidget()
        value_from_datadict = widget.value_from_datadict(data, files, field_name)
        self.assertEqual(Keyword.objects.all()[0].id, int(value_from_datadict[0]))
