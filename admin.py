from django.contrib import admin
from . import models


class YearAdmin(admin.ModelAdmin):
    pass

class DepartmentAdmin(admin.ModelAdmin):
    pass

class DegreeAdmin(admin.ModelAdmin):
    pass

class PersonAdmin(admin.ModelAdmin):
    pass

class CandidateAdmin(admin.ModelAdmin):
    pass

class CommitteeMemberAdmin(admin.ModelAdmin):
    pass

class LanguageAdmin(admin.ModelAdmin):
    pass

class KeywordAdmin(admin.ModelAdmin):
    pass

class ThesisAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Year, YearAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.Degree, DegreeAdmin)
admin.site.register(models.Person, PersonAdmin)
admin.site.register(models.Candidate, CandidateAdmin)
admin.site.register(models.CommitteeMember, CommitteeMemberAdmin)
admin.site.register(models.Language, LanguageAdmin)
admin.site.register(models.Keyword, KeywordAdmin)
admin.site.register(models.Thesis, ThesisAdmin)
