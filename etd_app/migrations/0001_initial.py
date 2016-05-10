# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('netid', models.CharField(max_length=100, unique=True, null=True, blank=True)),
                ('orcid', models.CharField(max_length=100, unique=True, null=True, blank=True)),
                ('last_name', models.CharField(max_length=190)),
                ('first_name', models.CharField(max_length=190)),
                ('middle', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('address_street', models.CharField(max_length=190)),
                ('address_city', models.CharField(max_length=190)),
                ('address_state', models.CharField(max_length=2)),
                ('address_zip', models.CharField(max_length=20)),
                ('phone', models.CharField(max_length=50)),
            ],
        ),
    ]
