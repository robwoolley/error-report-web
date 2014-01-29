#!/usr/bin/env python

# Add errors to database from client
#
# Copyright (C) 2013 Intel Corporation
# Author: Andreea Brandusa Proca <andreea.b.proca@intel.com>
#
# Licensed under the MIT license, see COPYING.MIT for details

import sys, os, json, re
from Post.models import Build, BuildFailure
from django.conf import settings
from datetime import datetime

class Parser:

    def __init__(self, data):
        self.data = data

    def parse(self):
        jsondata = json.loads(self.data)

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
        b=Build(DATE = datetime.now(), MACHINE = MACHINE_NAME, BRANCH = g.group(1), COMMIT = str(g.group(2)), TARGET = COMPONENT, DISTRO = DISTRO, NATIVELSBSTRING = NATIVELSBSTRING, BUILD_SYS = BUILD_SYS, TARGET_SYS = TARGET_SYS, NAME = NAME, EMAIL = EMAIL)
        b.save()
        failures = jsondata['failures']
        for fail in failures:
            if len(fail) > int(settings.MAX_UPLOAD_SIZE):
                return -1
            package = str(fail['package'])
            g = re.match(r'(.*)\-(\d.*)', package)
            f = BuildFailure(TASK = str(fail['task']), RECIPE = g.group(1), RECIPE_VERSION = g.group(2), ERROR_DETAILS = str(fail['log']), BUILD = b)
            f.save()
        return b.id
