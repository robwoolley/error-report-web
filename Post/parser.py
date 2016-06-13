#!/usr/bin/env python

# Add errors to database from client
#
# Copyright (C) 2013 Intel Corporation
# Author: Andreea Brandusa Proca <andreea.b.proca@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import json, re
from Post.models import Build, BuildFailure, ErrorType
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse

class Parser:

    def __init__(self, data):
        self.data = data

    # returns true if the values contain '<' char
    # Ignore the failures field (which is an array anyway)
    def contains_tags (self, data):
        for key,val in data.items():
            if key == 'failures':
                continue

            if '<' in val:
                return True
        return False

    def parse(self, request):
        build_fails_logged = []

        try:
            jsondata = json.loads(self.data)
        except:
             return  { 'error' : 'Invalid json' }

        if self.contains_tags(jsondata) == True:
            return  { 'error' : 'Invalid characters in json' }

        b = Build.objects.create()
        try:
            b.MACHINE = str(jsondata['machine'])
            b.NATIVELSBSTRING = str(jsondata['nativelsb'])
            b.TARGET_SYS = str(jsondata['target_sys'])
            b.BRANCH_COMMIT = str(jsondata['branch_commit'])
            b.COMPONENT = str(jsondata['component'])
            b.BUILD_SYS = str(jsondata['build_sys'])
            b.DISTRO = str(jsondata['distro'])
            b.NAME = str(jsondata['username'])
            b.EMAIL = str(jsondata['email'])
            b.LINK_BACK = jsondata.get("link_back", None)
            b.ERROR_TYPE = jsondata.get("error_type", ErrorType.RECIPE)

            # Extract the branch and commit
            g = re.match(r'(.*): (.*)', jsondata['branch_commit'])

            if g and g.lastindex == 2:
                b.BRANCH = g.group(1)
                b.COMMIT = g.group(2)
            else:
                b.BRANCH = "unknown"
                b.COMMIT = "unknown"

            b.DATE = timezone.now()

            b.save()
            failures = jsondata['failures']
        except Exception as e:
            return { 'error' : "Problem reading json payload, %s" % e.message }

        for fail in failures:
            if len(fail) > int(settings.MAX_UPLOAD_SIZE):
                build_fails_logged.append({ 'id': -1, 'error' : "The size of the upload is too large" })
                continue

            #Extract the recipe and version
            package = str(fail['package'])
            g = re.match(r'(.*)\-(\d.*)', package)
            if g and g.lastindex == 2:
                recipe = g.group(1)
                recipe_version = g.group(2)
            else:
                recipe = package
                recipe_version = "unknown"

            f = BuildFailure(TASK = str(fail['task']), RECIPE = recipe, RECIPE_VERSION = recipe_version, ERROR_DETAILS = fail['log'].encode('utf-8'), BUILD = b)

            f.save()

            url = request.build_absolute_uri(reverse('details', args=[f.id]))

            build_fails_logged.append({ 'id' : f.id,
                                        'url' : url,
                                      })

        build_url = request.build_absolute_uri(reverse('build_errors', args=[b.id]))

        num_similar_errors = f.get_similar_fails_count()

        result = { 'build_id' : b.id,
                   'build_url' : build_url,
                   'failures' : build_fails_logged,
                   'num_similar_errors' : num_similar_errors,
                 }

        if num_similar_errors > 0:
            similars_url = request.build_absolute_uri(reverse('similar', args=[f.id]))
            result['similar_errors_url'] = similars_url

        return result
