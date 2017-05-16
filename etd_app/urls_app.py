from __future__ import unicode_literals
from django.conf.urls import url
from . import views


urlpatterns = [
        url(regex=r'^$', view=views.home, name='home'),
        url(regex=r'^index.php$', view=views.redirect_to_home, name='redirect_to_home'),
        url(regex=r'^login/$', view=views.login, name='login'),
        url(regex=r'^overview/$', view=views.overview, name='overview'),
        url(regex=r'^faq/$', view=views.faq, name='faq'),
        url(regex=r'^copyright/$', view=views.copyright, name='copyright'),
        url(regex=r'^register/$', view=views.register, name='register'),
        url(regex=r'^candidate/$', view=views.candidate_home, name='candidate_home'),
        url(regex=r'^candidate/upload/$', view=views.candidate_upload, name='candidate_upload'),
        url(regex=r'^candidate/metadata/$', view=views.candidate_metadata, name='candidate_metadata'),
        url(regex=r'^candidate/committee/$', view=views.candidate_committee, name='candidate_committee'),
        url(regex=r'^candidate/committee/(?P<cm_id>\d+)/remove/$', view=views.candidate_committee_remove, name='candidate_committee_remove'),
        url(regex=r'^candidate/preview/$', view=views.candidate_preview_submission, name='candidate_preview_submission'),
        url(regex=r'^candidate/submit/$', view=views.candidate_submit, name='candidate_submit'),
        url(regex=r'^review/$', view=views.staff_home, name='staff_home'),
        url(
            regex=r'^review/(?P<status>all|in_progress|awaiting_gradschool|dissertation_rejected|paperwork_incomplete|complete)/$',
            view=views.staff_view_candidates,
            name='review_candidates'),
        url(regex=r'^review/(?P<candidate_id>\d+)/$', view=views.staff_approve, name='approve'),
        url(regex=r'^review/(?P<candidate_id>\d+)/format_post/$', view=views.staff_format_post, name='format_post'),
        url(regex=r'^(?P<candidate_id>\d+)/abstract/$', view=views.view_abstract, name='abstract'),
        url(regex=r'^(?P<candidate_id>\d+)/view_file/$', view=views.view_file, name='view_file'),
        url(regex=r'^autocomplete/keywords/$', view=views.autocomplete_keywords, name='autocomplete_keywords'),
    ]
