from __future__ import unicode_literals
import logging
from django.contrib import admin, messages
from . import models
from .ingestion import ThesisIngester, IngestException


logger = logging.getLogger('etd')


class ThesisAdmin(admin.ModelAdmin):

    list_display = ['id', 'candidate', 'original_file_name', 'status', 'pid']
    list_filter = ['status']
    actions = ['ingest']

    def ingest(self, request, queryset):
        for thesis in queryset:
            ingester = ThesisIngester(thesis)
            try:
                ingester.ingest()
            except IngestException as ie:
                msg = 'Error ingesting thesis %s' % thesis.id
                msg = '%s\n%s' % (msg, ie)
                logger.error(msg)
                messages.error('Error ingesting thesis %s. Check the log and re-ingest.' % thesis.id)
    ingest.short_description = 'Ingest selected theses'


admin.site.register(models.Department)
admin.site.register(models.Degree)
admin.site.register(models.Person)
admin.site.register(models.GradschoolChecklist)
admin.site.register(models.Candidate)
admin.site.register(models.CommitteeMember)
admin.site.register(models.Language)
admin.site.register(models.Keyword)
admin.site.register(models.Thesis, ThesisAdmin)
