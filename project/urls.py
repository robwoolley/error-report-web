# error-reporting-tool - URL definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.generic import TemplateView
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^Errors/Search/Latest/$', 'Post.views.search', {'template_name' : 'latest-errors.html'}, name= "latest_errors"),
    url(r'^Errors/Search/Args/$', 'Post.views.search', {'template_name' : 'search-details.html'}, name = "entry_args"),
    url(r'^Errors/Search/(?P<items>\d+)/(?P<page>\d+)/(?P<query>\w+)/', 'Post.views.search', {'template_name' : 'search-details.html'}, name = "entry"),
    url(r'^Errors/Search/(?P<page>\d+)/(?P<query>\d+)/', 'Post.views.viewEntry', {'template_name' : 'search-details.html'}),
    url(r'^Errors/Search/(?P<page>\d+)/(?P<query>\d+)/', 'Post.views.returnUrl', name = "your_entry"),
    url(r'^Errors/Search/Details/(?P<pk>\d+)/(?P<page>\w+)/(?P<items>\d+)/(?P<query>.+)', 'Post.views.searchDetails', {'template_name' : 'error-details.html'}, name='id'),
    url(r'^Errors/Statistics/(?P<key>\w+)', 'Post.views.chart', {'template_name' : 'home.html'}, name= "statistics"),
    url(r'^Errors/ErrorPage/$', TemplateView.as_view(template_name="error-page.html"), name ="errorpage"),
    url(r'^ClientPost/', 'Post.views.addData'),
    url(r'^Errors/', TemplateView.as_view(template_name="home.html"), name = "main"),
)
