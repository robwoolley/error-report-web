# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def add_lev_distance_data(apps, schema_editor):
    BuildFailure = apps.get_model("Post", "BuildFailure")
    for buildfail in BuildFailure.objects.all():
        buildfailure.save(recalc_lev_distance=True)

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
    ]
