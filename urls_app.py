from django.conf.urls import url
from . import views


urlpatterns = [
        url(regex=r'^$', view=views.home, name='home'),
        url(regex=r'^overview/$', view=views.overview, name='overview'),
        url(regex=r'^faq/$', view=views.faq, name='faq'),
        url(regex=r'^tutorials/$', view=views.tutorials, name='tutorials'),
        url(regex=r'^copyright/$', view=views.copyright, name='copyright'),
    ]
