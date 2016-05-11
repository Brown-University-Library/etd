# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0017_thesis_date_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='thesis',
            name='date_accepted',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='thesis',
            name='date_rejected',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
