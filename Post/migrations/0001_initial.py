# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('DATE', models.DateTimeField(null=True, verbose_name=b'Submit date', blank=True)),
                ('MACHINE', models.CharField(max_length=50)),
                ('BRANCH', models.CharField(max_length=200)),
                ('COMMIT', models.CharField(max_length=200)),
                ('TARGET', models.CharField(max_length=100)),
                ('DISTRO', models.CharField(max_length=50)),
                ('NATIVELSBSTRING', models.CharField(max_length=100)),
                ('BUILD_SYS', models.CharField(max_length=200)),
                ('TARGET_SYS', models.CharField(max_length=200)),
                ('NAME', models.CharField(max_length=50)),
                ('EMAIL', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BuildFailure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('TASK', models.CharField(max_length=200)),
                ('RECIPE', models.CharField(max_length=250)),
                ('RECIPE_VERSION', models.CharField(max_length=200)),
                ('ERROR_DETAILS', models.TextField(max_length=5242880)),
                ('BUILD', models.ForeignKey(to='Post.Build')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
