from django.conf.urls import url
from . import views


urlpatterns = [
        url(regex=r'^$', view=views.home, name='home'),
        url(regex=r'^overview/$', view=views.overview, name='overview'),
        url(regex=r'^tutorials/$', view=views.tutorials, name='tutorials'),
    ]
