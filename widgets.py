from django.forms.widgets import SelectMultiple
from django.utils.encoding import force_text
from .models import Keyword


ID_VAL_SEPARATOR = u'\t'
FAST_URI = u'http://id.worldcat.org/fast'


class KeywordSelect2TagWidget(SelectMultiple):

    queryset = Keyword.objects.all()

    def _get_value_text(self, value):
        #from the widget value, get the string that would go in the Keyword.text field
        if ID_VAL_SEPARATOR in value:
            value = value.split(ID_VAL_SEPARATOR, 1)[1]
        return Keyword.normalize_text(value)

    def _create_new_keyword(self, value):
        if ID_VAL_SEPARATOR in value:
            fast_id, kw_text = value.split(ID_VAL_SEPARATOR, 1)
            fast_id = fast_id.replace('fst', '')
            return self.queryset.create(text=kw_text, authority='fast',
                    authority_uri=FAST_URI, value_uri='%s/%s' % (FAST_URI, fast_id))
        else:
            return self.queryset.create(text=value)

    def value_from_datadict(self, data, files, field_name):
        values = super(KeywordSelect2TagWidget, self).value_from_datadict(data, files, field_name)
        cleaned_values = []
        for val in [val for val in values if val]:
            try:
                qs = self.queryset.filter(**{'pk__in': val})
                cleaned_values.append(val)
            except ValueError:
                #val is some text the user just typed
                #it might be in the db already, just not found because it's composed instead of decomposed
                kw_text = self._get_value_text(val)
                try:
                    found_keyword = self.queryset.get(text=kw_text)
                    #we found the keyword, so add this id to cleaned_values
                    cleaned_values.append(found_keyword.id)
                except Keyword.DoesNotExist:
                    created_keyword = self._create_new_keyword(val)
                    cleaned_values.append(created_keyword.id)
        return cleaned_values
