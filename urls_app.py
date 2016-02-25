from django.conf.urls import url
from . import views


urlpatterns = [
        url(regex=r'^$', view=views.home, name='home'),
        url(regex=r'^overview/$', view=views.overview, name='overview'),
        url(regex=r'^faq/$', view=views.faq, name='faq'),
        url(regex=r'^tutorials/$', view=views.tutorials, name='tutorials'),
        url(regex=r'^copyright/$', view=views.copyright, name='copyright'),
        url(regex=r'^register/$', view=views.register, name='register'),
        url(regex=r'^candidate/$', view=views.candidate_home, name='candidate_home'),
        url(regex=r'^candidate/upload/$', view=views.candidate_upload, name='candidate_upload'),
    ]
