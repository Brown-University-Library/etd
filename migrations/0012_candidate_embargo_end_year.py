# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0011_auto_20160226_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='embargo_end_year',
            field=models.CharField(max_length=4, null=True, blank=True),
        ),
    ]
