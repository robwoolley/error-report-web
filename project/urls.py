# error-reporting-tool - URL definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from Post.views import results_mode
from Post.feed import LatestEntriesFeed
admin.autodiscover()

try:
    special_submitter = settings.SPECIAL_SUBMITTER['link']
except AttributeError:
    special_submitter = "none"

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^(?i)Errors/Latest/$', 'Post.views.search', { 'mode' : results_mode.LATEST }, name= "latest_errors"),
    url(r'^(?i)Errors/Latest/feed$', LatestEntriesFeed(), name="errors_feed"),
    url(r'^(?i)Errors/Latest/'+special_submitter+'/$', 'Post.views.search', { 'mode' : results_mode.SPECIAL_SUBMITTER}, name= "latest_autobuilder_errors"),
    url(r'^(?i)Errors/Latest/'+special_submitter+'/feed$', LatestEntriesFeed(results_mode.SPECIAL_SUBMITTER), name="special_submitter_errors_feed"),
    url(r'^(?i)Errors/Search/$', 'Post.views.search', {'mode' : results_mode.SEARCH }, name = "errors_search"),
    url(r'^(?i)Errors/Build/(?P<build_id>\d+)/$', 'Post.views.search', { 'mode' : results_mode.BUILD }, name= "build_errors"),
    url(r'^(?i)Errors/Details/(?P<fail_id>\d+)/$', 'Post.views.details', name='details'),
    url(r'^(?i)Errors/SimilarTo/(?P<fail_id>\d+)/$', 'Post.views.search', { 'mode' : results_mode.SIMILAR_TO }, name='similar'),
    url(r'^(?i)Errors/Statistics/(?P<key>\w+)', 'Post.views.chart', {'template_name' : 'home.html'}, name= "statistics"),
    url(r'^(?i)ClientPost/$', 'Post.views.addData'),
    url(r'^(?i)ClientPost/JSON/$', 'Post.views.addData', { 'return_json' : True }),
    url(r'^(?i)Errors/$', 'Post.views.default', name="main"),
    url(r'^(?i)Statistics/$', TemplateView.as_view(template_name="home.html"), name = "statistics"),
    url(r'^$', RedirectView.as_view(pattern_name="main")),
    # Url for backwards compatibility with old search links
    url(r'^Errors/Search/Args/$', RedirectView.as_view(pattern_name="Post.views.search",query_string=True), {'mode':results_mode.SEARCH }),
)
