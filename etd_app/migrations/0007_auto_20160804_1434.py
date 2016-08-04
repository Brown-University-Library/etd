# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0006_auto_20160718_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thesis',
            name='num_body_pages',
            field=models.PositiveSmallIntegerField(null=True, blank=True),
        ),
    ]
