# error-reporting-tool - model definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from datetime import datetime

# Create your models here.
class Build(models.Model):
    DATE = models.DateTimeField('Submit date', blank=True, null=True)
    MACHINE = models.CharField(max_length=50)
    BRANCH = models.CharField(max_length=200)
    COMMIT =  models.CharField(max_length=200)
    TARGET = models.CharField(max_length=100)
    DISTRO = models.CharField(max_length=50)
    NATIVELSBSTRING = models.CharField(max_length=100)
    BUILD_SYS = models.CharField(max_length=200)
    TARGET_SYS = models.CharField(max_length=200)
    NAME = models.CharField(max_length=50)
    EMAIL = models.CharField(max_length=50)

class BuildFailure(models.Model):
    TASK = models.CharField(max_length=200)
    RECIPE= models.CharField(max_length=250)
    RECIPE_VERSION = models.CharField(max_length=200)
    ERROR_DETAILS = models.TextField(max_length=int(settings.MAX_UPLOAD_SIZE))
    BUILD = models.ForeignKey(Build)
