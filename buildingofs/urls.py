from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = patterns('',
    url(r'^$', views.HomepageView.as_view(), name='home'),
    url(r'^blog/', include('buildingofs.blog.urls')),

    url(r'^login/$', auth_views.login, {'template_name': 'account/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'account/logout.html'}, name='logout'),
)
