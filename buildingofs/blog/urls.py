from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    url(r'^(?P<slug>[\w\.-]+)/$', views.PostView.as_view(), name='view-post'),
)
