# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0002_department_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(unique=True, max_length=190),
        ),
        migrations.AlterField(
            model_name='year',
            name='year',
            field=models.CharField(unique=True, max_length=5),
        ),
    ]
