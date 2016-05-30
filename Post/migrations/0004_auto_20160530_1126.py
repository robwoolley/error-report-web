# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Post', '0003_auto_20150603_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buildfailure',
            name='TASK',
            field=models.CharField(max_length=1024),
            preserve_default=True,
        ),
    ]
