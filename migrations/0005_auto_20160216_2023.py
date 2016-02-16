# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0004_degree'),
    ]

    operations = [
        migrations.AlterField(
            model_name='degree',
            name='abbreviation',
            field=models.CharField(unique=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='degree',
            name='name',
            field=models.CharField(unique=True, max_length=190),
        ),
    ]
