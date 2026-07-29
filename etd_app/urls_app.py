from django.urls import re_path
from . import views


urlpatterns = [
        re_path(r'^$', view=views.home, name='home'),
        re_path(r'^index.php$', view=views.redirect_to_home, name='redirect_to_home'),
        re_path(r'^login/$', view=views.login, name='login'),
        re_path(r'^overview/$', view=views.overview, name='overview'),
        re_path(r'^faq/$', view=views.faq, name='faq'),
        re_path(r'^copyright/$', view=views.copyright, name='copyright'),
        re_path(r'^register/$', view=views.register, name='register'), #creates new candidate profile (could be multiple per person)
        re_path(r'^candidate/(?P<candidate_id>\d+)/$', view=views.candidate_home, name='candidate_home'),
        re_path(r'^candidate/$', view=views.candidate_home, name='candidate_home'),
        re_path(r'^candidate/(?P<candidate_id>\d+)/profile/$', view=views.candidate_profile, name='candidate_profile'),
        re_path(r'^candidate/(?P<candidate_id>\d+)/upload/$', view=views.candidate_upload, name='candidate_upload'),
        re_path(r'^candidate/(?P<candidate_id>\d+)/metadata/$', view=views.candidate_metadata, name='candidate_metadata'),
        re_path(r'^candidate/(?P<candidate_id>\d+)/committee/$', view=views.candidate_committee, name='candidate_committee'),
        re_path(r'^candidate/(?P<candidate_id>\d+)/committee/(?P<cm_id>\d+)/remove/$', view=views.candidate_committee_remove, name='candidate_committee_remove'),
        re_path(r'^candidate/(?P<candidate_id>\d+)/preview/$', view=views.candidate_preview_submission, name='candidate_preview_submission'),
        re_path(r'^candidate/(?P<candidate_id>\d+)/submit/$', view=views.candidate_submit, name='candidate_submit'),
        re_path(r'^review/$', view=views.staff_home, name='staff_home'),
        re_path(
            r'^review/(?P<status>all|in_progress|awaiting_gradschool|dissertation_rejected|paperwork_incomplete|complete)/$',
            view=views.staff_view_candidates,
            name='review_candidates'),
        re_path(r'^review/(?P<candidate_id>\d+)/$', view=views.staff_approve, name='approve'),
        re_path(r'^review/(?P<candidate_id>\d+)/format_post/$', view=views.staff_format_post, name='format_post'),
        re_path(r'^(?P<candidate_id>\d+)/abstract/$', view=views.view_abstract, name='abstract'),
        re_path(r'^(?P<candidate_id>\d+)/view_file/$', view=views.view_file, name='view_file'),
        re_path(r'^autocomplete/keywords/$', view=views.autocomplete_keywords, name='autocomplete_keywords'),
    ]
