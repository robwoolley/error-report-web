# error-reporting-tool - URL definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from Post.views import results_mode
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^(?i)Errors/Latest/$', 'Post.views.search', { 'mode' : results_mode.LATEST }, name= "latest_errors"),
    url(r'^(?i)Errors/Latest/Autobuilder/$', 'Post.views.search', { 'mode' : results_mode.AUTOBUILDER }, name= "latest_autobuilder_errors"),
    url(r'^(?i)Errors/Search/$', 'Post.views.search', {'mode' : results_mode.SEARCH }, name = "errors_search"),
    url(r'^(?i)Errors/Build/(?P<build_id>\d+)/$', 'Post.views.search', { 'mode' : results_mode.BUILD }, name= "build_errors"),
    url(r'^(?i)Errors/Details/(?P<fail_id>\d+)/$', 'Post.views.details', {'template_name' : 'error-details.html'}, name='details'),
    url(r'^(?i)Errors/Statistics/(?P<key>\w+)', 'Post.views.chart', {'template_name' : 'home.html'}, name= "statistics"),
    url(r'^Errors/ErrorPage/$', TemplateView.as_view(template_name="error-page.html"), name ="errorpage"),
    url(r'^(?i)ClientPost/', 'Post.views.addData'),
    url(r'^(?i)ClientPost/JSON/$', 'Post.views.addData', { 'return_json' : True }),
    url(r'^(?i)Errors/$', TemplateView.as_view(template_name="home.html"), name = "main"),
)
