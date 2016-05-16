# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0030_auto_20160516_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='bdr_collection_id',
            field=models.CharField(max_length=20, unique=True, null=True, blank=True),
        ),
    ]
