# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Post', '0004_auto_20160530_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='ERROR_TYPE',
            field=models.CharField(default=b'recipe', max_length=20, choices=[(b'recipe', b'Recipe'), (b'core', b'Core'), (b'bitbake-selftest', b'Bitbake selftest'), (b'oe-selftest', b'OE selftest')]),
        ),
    ]
