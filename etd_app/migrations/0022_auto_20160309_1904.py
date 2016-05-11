# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0021_auto_20160309_1851'),
    ]

    operations = [
        migrations.AddField(
            model_name='thesis',
            name='num_body_pages',
            field=models.CharField(max_length=10, blank=True),
        ),
        migrations.AddField(
            model_name='thesis',
            name='num_prelim_pages',
            field=models.CharField(max_length=10, blank=True),
        ),
    ]
