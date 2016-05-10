# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0025_auto_20160309_2136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='thesis',
        ),
        migrations.AddField(
            model_name='thesis',
            name='candidate',
            field=models.OneToOneField(default=1, to='etd_app.Candidate'),
            preserve_default=False,
        ),
    ]
