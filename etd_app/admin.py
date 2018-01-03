import logging
from django.contrib import admin, messages
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from . import models
from .forms import AdminThesisForm, AdminCandidateForm
from .ingestion import ThesisIngester, IngestException


logger = logging.getLogger('etd')


class ThesisAdmin(admin.ModelAdmin):

    list_display = ['id', 'candidate', 'original_file_name', 'status', 'pid']
    list_filter = ['status']
    actions = ['ingest']
    form = AdminThesisForm

    def ingest(self, request, queryset):
        for thesis in queryset:
            ingester = ThesisIngester(thesis)
            try:
                ingester.ingest()
            except IngestException as ie:
                msg = 'Error ingesting thesis %s' % thesis.id
                msg = '%s\n%s' % (msg, ie)
                logger.error(msg)
                messages.error(request, 'Error ingesting thesis %s. Check the log and re-ingest.' % thesis.id)
    ingest.short_description = 'Ingest selected theses'


class PersonAdmin(admin.ModelAdmin):

    list_display = ['id', 'netid', 'last_name', 'first_name', 'email', 'created', 'modified']


class CandidateAdmin(admin.ModelAdmin):

    form = AdminCandidateForm


class DepartmentResource(resources.ModelResource):

    class Meta:
        model = models.Department
        fields = ('id', 'name', 'bdr_collection_id')


class DepartmentAdmin(ImportExportModelAdmin):

    resource_class = DepartmentResource


class KeywordAdmin(admin.ModelAdmin):

    list_display = ['id', 'text', 'search_text', 'authority', 'authority_uri', 'value_uri']


admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.Degree)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.FormatChecklist)
admin.site.register(models.GradschoolChecklist)
admin.site.register(models.Candidate, CandidateAdmin)
admin.site.register(models.CommitteeMember)
admin.site.register(models.Language)
admin.site.register(models.Keyword, KeywordAdmin)
admin.site.register(models.Thesis, ThesisAdmin)
