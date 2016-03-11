from django.utils.encoding import force_text
from django_select2.forms import ModelSelect2TagWidget
from .models import Keyword


class KeywordSelect2TagWidget(ModelSelect2TagWidget):

    queryset = Keyword.objects.all()

    def value_from_datadict(self, data, files, field_name):
        values = super(KeywordSelect2TagWidget, self).value_from_datadict(data, files, field_name)
        cleaned_values = []
        for val in values:
            try:
                qs = self.queryset.filter(**{'pk__in': val})
                cleaned_values.append(val)
            except ValueError:
                #val is some text the user just typed
                #it might be in the db already, just not found because it's composed instead of decomposed
                search_text = Keyword.normalize_text(val)
                try:
                    found_keyword = self.queryset.get(text=search_text)
                    #we found the keyword, so add this id to cleaned_values
                    cleaned_values.append(found_keyword.id)
                except Keyword.DoesNotExist:
                    created_keyword = self.queryset.create(text=val)
                    cleaned_values.append(created_keyword.id)
        return cleaned_values
