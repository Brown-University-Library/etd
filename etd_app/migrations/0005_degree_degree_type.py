# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0004_auto_20160615_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='degree',
            name='degree_type',
            field=models.CharField(default='doctorate', max_length=20, choices=[('doctorate', 'Doctorate'), ('masters', 'Masters')]),
        ),
    ]
