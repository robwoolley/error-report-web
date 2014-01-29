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

class Statistics:

    def create_statistic(self, itemList, field):
        names = []
        total = []
        statistic_dict = {}
        i=0
        for e in itemList:
            values=[]
            for itemValue in e.values():
                values.append(itemValue)
            try:
                t = int(values[1])
                name = values[0]
            except ValueError:
                t = int(values[0])
                name = values[1]
            total.append(t)
            names.append(name)
        statistic_dict["names"] = names
        statistic_dict["values"] = total
        return statistic_dict

    def chart_statistics(self, string):
        startdate = datetime.now()
        enddate = startdate - timedelta(days=30)
        if string == "MACHINE":
            machines = Build.objects.filter(DATE__range=[enddate, startdate]).values('MACHINE').annotate(dcount=Count('MACHINE'))
            items = list(machines)
            return self.create_statistic(items, "MACHINE")
        elif string == "BRANCH":
            branch = Build.objects.filter(DATE__range=[enddate, startdate]).values('BRANCH').annotate(dcount=Count('BRANCH'))
            items = list(branch)
            return self.create_statistic(items, "BRANCH")
        elif string == "COMMIT":
            branch = Build.objects.filter(DATE__range=[enddate, startdate]).values('COMMIT').annotate(dcount=Count('COMMIT'))
            items = list(branch)
            return self.create_statistic(items, "COMMIT")
        elif string == "TARGET":
            images = Build.objects.filter(DATE__range=[enddate, startdate]).values('TARGET').annotate(dcount=Count('TARGET'))
            items = list(images)
            return self.create_statistic(items, "TARGET")
        elif string == "RECIPE":
            errors = BuildFailure.objects.filter(BUILD__DATE__range=[enddate, startdate]).values('RECIPE').annotate(dcount=Count('RECIPE'))
            items = list(errors)
            return self.create_statistic(items, "RECIPE")
        elif string =="DISTRO":
            errors = Build.objects.filter(DATE__range=[enddate, startdate]).values('DISTRO').annotate(dcount=Count('DISTRO'))
            items = list(errors)
            return self.create_statistic(items, "DISTRO")
        elif string == "NATIVELSBSTRING":
            errors = Build.objects.filter(DATE__range=[enddate, startdate]).values('NATIVELSBSTRING').annotate(dcount=Count('NATIVELSBSTRING'))
            items = list(errors)
            return self.create_statistic(items, "NATIVELSBSTRING")
        elif string == "TARGET_SYS":
            errors = Build.objects.filter(DATE__range=[enddate, startdate]).values('TARGET_SYS').annotate(dcount=Count('TARGET_SYS'))
            items = list(errors)
            return self.create_statistic(items, "TARGET_SYS")
        elif string == "BUILD_SYS":
            errors = Build.objects.filter(DATE__range=[enddate, startdate]).values('BUILD_SYS').annotate(dcount=Count('BUILD_SYS'))
            items = list(errors)
        return {}
