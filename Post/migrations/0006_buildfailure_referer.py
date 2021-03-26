# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Post', '0005_build_error_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildfailure',
            name='REFERER',
            field=models.CharField(default=b'NOT_VISITED', max_length=14, choices=[(b'NO_REFERER', b'no_referer'), (b'OTHER', b'other'), (b'NOT_VISITED', b'not_visited')]),
        ),
    ]
