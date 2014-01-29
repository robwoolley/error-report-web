#!/usr/bin/env python

# Get information from database
#
# Copyright (C) 2013 Intel Corporation
# Author: Andreea Brandusa Proca <andreea.b.proca@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import sys, os
from Post.models import Build, BuildFailure
from createStatistics import Statistics

class Info:

    def getItemCategory(self, string):
        string = string.lower()
        for i in range(0, Build.objects.values().__len__()):
            index = -1
            values = Build.objects.values()[i].values()
            for j in range(0, len(values)):
                if str(values[j]).lower().find(string) != -1:
                    index = j
                    break
            if index != -1:
                category = Build.objects.values()[i].keys().__getitem__(index)
                return category
        for i in range(0, BuildFailure.objects.values().__len__()):
            index = -1
            values = BuildFailure.objects.values()[i].values()
            for j in range(0, len(values)):
                if str(values[j]).lower().find(string) != -1:
                    index = j
                if index != -1:
                    category = BuildFailure.objects.values()[i].keys().__getitem__(index)
                    return category
        return ""

    def getSearchResult(self, string):
        results = []
        category = ""
        if string == "all":
            results.append(BuildFailure.objects.all())
            return results
        special_characters = ['.', '-', '&', '?']
        search_list = string.split()
        for i in range(len(search_list)):
            string = search_list[i]
            for c in special_characters:
                if c in string and len(search_list) == 1:
                    if i == len(search_list) - 1:
                        return results
                    i = i+1
                    string = search_list[i]
            try:
                build_id = int(string)
            except ValueError:
                category = self.getItemCategory(string)
            else:
                try:
                    build = Build.objects.get(id = build_id)
                    results.append(self.getBfByID(build))
                except:
                    pass
            if category == "MACHINE":
                build = Build.objects.filter(MACHINE__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "TARGET":
                build = Build.objects.filter(TARGET__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "RECIPE":
                buildFs = BuildFailure.objects.filter(RECIPE__icontains = string)
                results.append(buildFs)
            elif category == "RECIPE_VERSION":
                buildFs = BuildFailure.objects.filter(RECIPE_VERSION__icontains = string)
                results.append(buildFs)
            elif category == "BRANCH":
                build = Build.objects.filter(BRANCH__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "COMMIT":
                build = Build.objects.filter(COMMIT__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "DISTRO":
                build = Build.objects.filter(DISTRO__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "TARGET_SYS":
                build = Build.objects.filter(TARGET_SYS__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "NATIVELSBSTRING":
                build = Build.objects.filter(NATIVELSBSTRING__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "NAME":
                build = Build.objects.filter(NAME__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "EMAIL":
                build = Build.objects.filter(EMAIL__icontains = string)
                results.append(self.getBuildFailures(build))
            elif category == "TASK":
                buildFs = BuildFailure.objects.filter(TASK__icontains = string)
                results.append(buildFs)
        return results

    def getBuildFailures(self, results):
        bfs=[]
        for i in range(0, len(results)):
            bf = BuildFailure.objects.filter(BUILD=results[i].id)
            bfs.append(bf)
        return bfs

    def getBfByID(self, b):
        bfs=[]
        bfs.append(BuildFailure.objects.filter(BUILD=b.id))
        return bfs

    def getBFDetails(self, idbf):
        return BuildFailure.objects.filter(id=idbf)
