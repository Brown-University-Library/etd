# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0028_auto_20160314_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='embargo_end_year',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='year',
            field=models.IntegerField(),
        ),
        migrations.DeleteModel(
            name='Year',
        ),
    ]
