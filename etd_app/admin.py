from __future__ import unicode_literals
from django.contrib import admin
from . import models
from .ingestion import ThesisIngester


class ThesisAdmin(admin.ModelAdmin):

    actions = ['ingest']

    def ingest(self, request, queryset):
        for thesis in queryset:
            ingester = ThesisIngester(thesis)
            intester.ingest()
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
