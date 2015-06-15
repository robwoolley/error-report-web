# error-reporting-tool - URL definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from Post.models import BuildFailure
from Post.views import results_mode
from django.conf import settings
import re

class LatestEntriesFeed(Feed):
    title = "Latest errors"
    description = "Latest Yocto project errors reported."
    link = "/"

    def __init__(self, mode=None):
        super(Feed, self).__init__()
        self.mode = mode
        self.limit = 10

    def items(self):
        if self.mode == results_mode.SPECIAL_SUBMITTER and hasattr(settings,"SPECIAL_SUBMITTER"):
            #Special submitter mode see settings.py to enable
            name = settings.SPECIAL_SUBMITTER['name']
            queryset = BuildFailure.objects.order_by('-BUILD__DATE').filter(BUILD__NAME__istartswith=name)[:self.limit]

        else:
            queryset = BuildFailure.objects.order_by('-BUILD__DATE')[:self.limit]
        return queryset


    def item_title(self, item):
        title = "Error in %s running %s" % (item.RECIPE, item.TASK)
        return title

    def item_description(self, item):
        # Although these are valid utf-8 chars control codes e.g. 000 0002 are
        # not allowed in RSS/xml.
        text = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\u10000-\u10FFFF]+', '', item.ERROR_DETAILS)
        return "<pre>%s</pre>" % text

    def item_link(self, item):
        return reverse('details', args=[item.pk])
