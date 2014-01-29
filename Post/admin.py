# error reporting tool - admin interface definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.contrib import admin
from Post.models import Build
from Post.models import BuildFailure

admin.site.register(Build)
admin.site.register(BuildFailure)
