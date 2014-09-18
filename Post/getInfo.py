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

    def getFilteredList(self, results, filter_string):
        arg_list = [arg.strip() for arg in filter_string.split(':')]
        if arg_list[1] == "RECIPE":
            return filter(lambda x: x.RECIPE == arg_list[0], results)
        elif arg_list[1] == "TASK":
            return filter(lambda x: x.TASK == arg_list[0], results)
        elif arg_list[1] == "MACHINE":
            return filter(lambda x: x.BUILD.MACHINE == arg_list[0], results)
        elif arg_list[1] == "DISTRO":
            return filter(lambda x: x.BUILD.DISTRO == arg_list[0], results)
        elif arg_list[1] == "BUILD_SYS":
            return filter(lambda x: x.BUILD.BUILD_SYS == arg_list[0], results)
        elif arg_list[1] == "TARGET_SYS":
            return filter(lambda x: x.BUILD.TARGET_SYS == arg_list[0], results)
        elif arg_list[1] == "NATIVELSBSTRING":
            return filter(lambda x: x.BUILD.NATIVELSBSTRING == arg_list[0], results)
        elif arg_list[1] == "BRANCH":
            return filter(lambda x: x.BUILD.BRANCH == arg_list[0], results)
        elif arg_list[1] == "NAME":
            return filter(lambda x: x.BUILD.NAME == arg_list[0], results)
        elif arg_list[1] == "COMMIT":
            return filter(lambda x: x.BUILD.COMMIT == arg_list[0], results)

    def getSearchResult(self, string, filter_string):
        results = []
        category = ""

        special_characters = ['.', '-', '&', '?']
        search_list = string.split()

        for i in range(len(search_list)):
            string = search_list[i]
            while string in special_characters:
                try:
                    string = search_list[i+1]
                    i = i + 1
                except:
                    results = self.flatten(results)
                    return (results, results)

            if string == "all":
                results.append(BuildFailure.objects.all())
                results = self.flatten(results)
                if filter_string:
                    return  (self.getFilteredList((results), filter_string), results)
                return (results, results)

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

            if category == "DATE":
                build = Build.objects.filter(DATE__icontains = string)
                results.append(self.getBuildFailures(build))
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

        results = self.flatten(results)
        if filter_string:
            return (self.getFilteredList(results, filter_string), results)

        return (results, results)

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

    def flatten(self, nested_list):
        res =  []
        for e in nested_list:
            if hasattr(e, "__iter__") and not isinstance(e, basestring):
                res.extend(self.flatten(e))
            else:
                res.append(e)
        return list(set(res))

