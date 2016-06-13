# error-reporting-tool - model definitions
#
# Copyright (C) 2013 Intel Corporation
#
# Licensed under the MIT license, see COPYING.MIT for details

from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from datetime import datetime

import Levenshtein

class ErrorType(object):
    RECIPE = 'recipe'
    CORE = 'core'
    BITBAKE_SELFTEST = 'bitbake-selftest'
    OE_SELFTEST = 'oe-selftest'

class InvalidErrorType(Exception):
    pass

# Create your models here.
class Build(models.Model):
    ERROR_TYPE_CHOICES = (
            (ErrorType.RECIPE, 'Recipe'),
            (ErrorType.CORE, 'Core'),
            (ErrorType.BITBAKE_SELFTEST, 'Bitbake selftest'),
            (ErrorType.OE_SELFTEST, 'OE selftest'),
    )

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
    LINK_BACK = models.TextField(max_length=300, blank=True, null=True)
    ERROR_TYPE = models.CharField(max_length=20, choices=ERROR_TYPE_CHOICES,
                                  default=ErrorType.RECIPE)

    def save(self, *args, **kwargs):
        if self.ERROR_TYPE not in [e_type[0] for e_type in
                                   self.ERROR_TYPE_CHOICES]:
            raise InvalidErrorType("Error type %s is not known" %
                                   self.ERROR_TYPE)

        super(Build, self).save(*args, **kwargs)

class BuildFailure(models.Model):
    TASK = models.CharField(max_length=1024)
    RECIPE= models.CharField(max_length=250)
    RECIPE_VERSION = models.CharField(max_length=200)
    ERROR_DETAILS = models.TextField(max_length=int(settings.MAX_UPLOAD_SIZE))
    BUILD = models.ForeignKey(Build)
    LEV_DISTANCE = models.IntegerField(blank=True, null=True)

    def get_similar_fails(self):
        if self.LEV_DISTANCE is None:
            return BuildFailure.objects.none()

        start = self.LEV_DISTANCE
        end = self.LEV_DISTANCE + settings.SIMILAR_FAILURE_DISTANCE

        query_set = BuildFailure.objects.filter(LEV_DISTANCE__range=(start,end)).exclude(id=self.id).filter(TASK=self.TASK)

        return query_set

    def get_similar_fails_count(self, count=False):

        return self.get_similar_fails().count()

    def calc_lev_distance(self):
        if BuildFailure.objects.all().count() == 0:
            return 0

        # Use the last 400 characters of the ERROR_DETAILS.
        # This is where the error message is likely to occour and
        # reduces the computational load on calculating the Levenshtein
        # distance.
        seed = BuildFailure.objects.first().ERROR_DETAILS[-400:]
        lv = Levenshtein.distance(str(seed), str(self.ERROR_DETAILS[-400:]))

        # Offset the distance calculated against the length of the error.
        return lv + len (self.ERROR_DETAILS)

    def save(self, *args, **kwargs):

        recalc_lev_distance = kwargs.pop('recalc_lev_distance', False)

        if self.LEV_DISTANCE == None or recalc_lev_distance:
            self.LEV_DISTANCE = self.calc_lev_distance()

        super(BuildFailure, self).save(*args, **kwargs)
