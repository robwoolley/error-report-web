# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import Levenshtein

def add_lev_distance_data(apps, schema_editor):

    BuildFailure = apps.get_model("Post", "BuildFailure")

    # copied from model see
    # https://docs.djangoproject.com/en/1.8/topics/migrations/#historical-models

    def calc_lev_distance(obj):
        if BuildFailure.objects.all().count() == 0:
            return 0

        # Use the last 400 characters of the ERROR_DETAILS.
        # This is where the error message is likely to occour and
        # reduces the computational load on calculating the Levenshtein
        # distance.
        seed = BuildFailure.objects.first().ERROR_DETAILS[-400:]
        lv = Levenshtein.distance(str(seed), str(obj.ERROR_DETAILS[-400:]))

        # Offset the distance calculated against the length of the error.
        return lv + len (obj.ERROR_DETAILS)


    offset = 0
    pagesize = 1000
    count = BuildFailure.objects.all().count()

    while offset < count:
        objs = BuildFailure.objects.all()[offset : offset + pagesize]
        for f in objs:
            if f.LEV_DISTANCE is None:
                f.LEV_DISTANCE = calc_lev_distance(f)
                f.save()

        del objs
        offset = offset + pagesize

def remove_lev_distance_data(apps, schema_editor):
    # Nothing to do at this point
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('Post', '0002_build_link_back'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildfailure',
            name='LEV_DISTANCE',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
       ),
        migrations.RunPython(add_lev_distance_data, remove_lev_distance_data),
    ]
