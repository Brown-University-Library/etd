# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0016_auto_20160307_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='thesis',
            name='date_submitted',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
