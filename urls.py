# SPDX-License-Identifier: MIT
#
# error-reporting-tool - URL definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.conf.urls import include, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from Post.views import results_mode
from Post.feed import LatestEntriesFeed
admin.autodiscover()

from Post import views

try:
    special_submitter = settings.SPECIAL_SUBMITTER['link']
except AttributeError:
    special_submitter = "none"

urlpatterns = [
    # Uncomment the admin/doc line below to enable admin documentation:
    #re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls),
    #re_path(r'^accounts/', include('registration.backends.default.urls')),
    re_path(r'^Errors/Latest/$', views.search, { 'mode' : results_mode.LATEST }, name= "latest_errors"),
    re_path(r'^Errors/Latest/feed$', LatestEntriesFeed(), name="errors_feed"),
    re_path(r'^Errors/Latest/'+special_submitter+'/$', views.search, { 'mode' : results_mode.SPECIAL_SUBMITTER}, name= "latest_autobuilder_errors"),
    re_path(r'^Errors/Latest/'+special_submitter+'/feed$', LatestEntriesFeed(results_mode.SPECIAL_SUBMITTER), name="special_submitter_errors_feed"),
    re_path(r'^Errors/Search/$', views.search, {'mode' : results_mode.SEARCH }, name = "errors_search"),
    re_path(r'^Errors/Build/(?P<build_id>\d+)/$', views.search, { 'mode' : results_mode.BUILD }, name= "build_errors"),
    re_path(r'^Errors/Details/(?P<fail_id>\d+)/$', views.details, name='details'),
    re_path(r'^Errors/SimilarTo/(?P<fail_id>\d+)/$', views.search, { 'mode' : results_mode.SIMILAR_TO }, name='similar'),
    re_path(r'^Errors/Statistics/(?P<key>\w+)', views.chart, {'template_name' : 'home.html'}, name= "statistics"),
    re_path(r'^ClientPost/$', views.addData),
    re_path(r'^ClientPost/JSON$', views.addData, { 'return_json' : True }),
    re_path(r'^ClientPost/JSON/$', views.addData, { 'return_json' : True }),
    re_path(r'^Errors/$', views.default, name="main"),
    re_path(r'^Statistics/$', TemplateView.as_view(template_name="home.html"), name = "statistics"),
    re_path(r'^$', RedirectView.as_view(pattern_name="main", permanent=True)),
    # Url for backwards compatibility with old search links
    re_path(r'^Errors/Search/Args/$', RedirectView.as_view(pattern_name="views.search",query_string=True,permanent=True), {'mode':results_mode.SEARCH }),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
