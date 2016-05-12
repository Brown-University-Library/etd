from __future__ import unicode_literals
from django.contrib import admin
from . import models


admin.site.register(models.Department)
admin.site.register(models.Degree)
admin.site.register(models.Person)
admin.site.register(models.GradschoolChecklist)
admin.site.register(models.Candidate)
admin.site.register(models.CommitteeMember)
admin.site.register(models.Language)
admin.site.register(models.Keyword)
admin.site.register(models.Thesis)
