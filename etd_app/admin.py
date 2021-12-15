import logging
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from . import models
from .forms import AdminThesisForm, AdminCandidateForm
from .ingestion import ThesisIngester, IngestException, find_theses_to_ingest


logger = logging.getLogger('etd')


class ReadyToIngestFilter(SimpleListFilter):
    title = 'Ready to Ingest'
    parameter_name = 'ready_to_ingest'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'yes':
            theses = find_theses_to_ingest()
            return queryset.filter(id__in=[t.id for t in theses])
        return queryset


class ThesisAdmin(admin.ModelAdmin):

    list_display = ['id', 'candidate', 'title', 'original_file_name', 'status', 'pid']
    list_filter = ['status', ReadyToIngestFilter]
    search_fields = ['candidate__person__last_name', 'candidate__person__first_name', 'title']
    actions = ['ingest', 'open_for_reupload']
    form = AdminThesisForm

    def ingest(self, request, queryset):
        for thesis in queryset:
            ingester = ThesisIngester(thesis)
            try:
                ingester.ingest()
            except IngestException as ie:
                msg = f'Error ingesting thesis {thesis.id}'
                msg = f'{msg}\n{ie}'
                logger.error(msg)
                messages.error(request, f'Error ingesting thesis {thesis.id}. Check the log and re-ingest.')
    ingest.short_description = 'Ingest selected theses'

    def open_for_reupload(self, request, queryset):
        for thesis in queryset:
            try:
                thesis.open_for_reupload()
            except models.ThesisException as te:
                messages.error(request, f'Error: {te}')
    open_for_reupload.short_description = 'Open For Re-Upload'


class PersonAdmin(admin.ModelAdmin):

    list_display = ['id', 'netid', 'last_name', 'first_name', 'email', 'created', 'modified']


class CandidateAdmin(admin.ModelAdmin):

    form = AdminCandidateForm
    list_display = ['id', 'person', 'year', 'department', 'embargo_end_year']
    search_fields = ['person__last_name', 'person__first_name']


class DepartmentResource(resources.ModelResource):

    class Meta:
        model = models.Department
        fields = ('id', 'name', 'bdr_collection_id')


class DepartmentAdmin(ImportExportModelAdmin):

    resource_class = DepartmentResource
    list_display = ['id', 'name', 'bdr_collection_id', 'bdr_collection_pid']


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
