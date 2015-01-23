#!/usr/bin/env python

# Add errors to database from client
#
# Copyright (C) 2013 Intel Corporation
# Author: Andreea Brandusa Proca <andreea.b.proca@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import json, re
from Post.models import Build, BuildFailure
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

    def parse(self, host):
        build_fails_logged = []

        try:
            jsondata = json.loads(self.data)
        except:
             return  { 'error' : 'Invalid json' }

        if self.contains_tags(jsondata) == True:
            return  { 'error' : 'Invalid characters in json' }

        try:
            MACHINE_NAME = str(jsondata['machine'])
            NATIVELSBSTRING = str(jsondata['nativelsb'])
            TARGET_SYS = str(jsondata['target_sys'])
            BRANCH_COMMIT = str(jsondata['branch_commit'])
            COMPONENT = str(jsondata['component'])
            BUILD_SYS = str(jsondata['build_sys'])
            DISTRO = str(jsondata['distro'])
            NAME = str(jsondata['username'])
            EMAIL = str(jsondata['email'])
            g = re.match(r'(.*): (.*)', str(BRANCH_COMMIT))
            b=Build(DATE = timezone.now(), MACHINE = MACHINE_NAME, BRANCH = g.group(1), COMMIT = str(g.group(2)), TARGET = COMPONENT, DISTRO = DISTRO, NATIVELSBSTRING = NATIVELSBSTRING, BUILD_SYS = BUILD_SYS, TARGET_SYS = TARGET_SYS, NAME = NAME, EMAIL = EMAIL)
            b.save()
            failures = jsondata['failures']
        except:
            return { 'error' : "Payload missing required fields" }

        for fail in failures:
            if len(fail) > int(settings.MAX_UPLOAD_SIZE):
                build_fails_logged.append({ 'id': -1, 'error' : "The size of the upload is too large" })
                continue
            package = str(fail['package'])
            g = re.match(r'(.*)\-(\d.*)', package)
            f = BuildFailure(TASK = str(fail['task']), RECIPE = g.group(1), RECIPE_VERSION = g.group(2), ERROR_DETAILS = str(fail['log']), BUILD = b)
            f.save()

            url = 'http://' + host + reverse('details', args=[f.id])

            build_fails_logged.append({ 'id' : f.id,
                                        'url' : url,
                                      })

        build_url = 'http://' + host + reverse('build_errors', args=[b.id])

        result = { 'build_id' : b.id,
                   'build_url' : build_url,
                   'failures' : build_fails_logged,
                 }

        return result
