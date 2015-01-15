#!/usr/bin/env python

# Create statistics. Update database.
#
# Copyright (C) 2013 Intel Corporation
# Author: Andreea Brandusa Proca <andreea.b.proca@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import sys, os
from Post.models import Build, BuildFailure
from django.db.models import Count
import re
from datetime import datetime, timedelta
from django import utils

class Statistics:

    def chart_statistics(self, string):
        startdate = utils.timezone.now()
        enddate = startdate - timedelta(days=14)
        if string == "DATE":
            date = Build.objects.filter(DATE__range=[enddate,
                                                     startdate]).values('DATE').annotate(dcount=Count('DATE'))[:6]
            items = list(date)
            return items
        if string == "MACHINE":
            machines = Build.objects.filter(DATE__range=[enddate, startdate]).values('MACHINE').annotate(dcount=Count('MACHINE')).order_by('-dcount')[:6]
            items = list(machines)
            return items
        elif string == "BRANCH":
            branch = Build.objects.filter(DATE__range=[enddate, startdate]).values('BRANCH').annotate(dcount=Count('BRANCH')).order_by('-dcount')[:6]
            items = list(branch)
            return items
        elif string == "COMMIT":
            branch = Build.objects.filter(DATE__range=[enddate, startdate]).values('COMMIT').annotate(dcount=Count('COMMIT')).order_by('-dcount')[:6]
            items = list(branch)
            return items
        elif string == "TARGET":
            images = Build.objects.filter(DATE__range=[enddate, startdate]).values('TARGET').annotate(dcount=Count('TARGET')).order_by('-dcount')[:6]
            items = list(images)
            return items
        elif string == "RECIPE":
            errors = BuildFailure.objects.filter(BUILD__DATE__range=[enddate, startdate]).values('RECIPE').annotate(dcount=Count('RECIPE')).order_by('-dcount')[:6]
            items = list(errors)
            return items
        elif string =="DISTRO":
            errors = Build.objects.filter(DATE__range=[enddate, startdate]).values('DISTRO').annotate(dcount=Count('DISTRO')).order_by('-dcount')[:6]
            items = list(errors)
            return items
        elif string == "NATIVELSBSTRING":
            errors = Build.objects.filter(DATE__range=[enddate, startdate]).values('NATIVELSBSTRING').annotate(dcount=Count('NATIVELSBSTRING')).order_by('-dcount')[:6]
            items = list(errors)
            return items;
        elif string == "TARGET_SYS":
            errors = Build.objects.filter(DATE__range=[enddate, startdate]).values('TARGET_SYS').annotate(dcount=Count('TARGET_SYS')).order_by('-dcount')[:6]
            items = list(errors)
            return items
        elif string == "BUILD_SYS":
            errors = Build.objects.filter(DATE__range=[enddate, startdate]).values('BUILD_SYS').annotate(dcount=Count('BUILD_SYS')).order_by('-dcount')[:6]
            items = list(errors)
            return items
        return {}
