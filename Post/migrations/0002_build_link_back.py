# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Post', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='LINK_BACK',
            field=models.TextField(max_length=300, null=True, blank=True),
            preserve_default=True,
        ),
    ]
