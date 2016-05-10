# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0010_auto_20160225_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thesis',
            name='language',
            field=models.ForeignKey(blank=True, to='etd_app.Language', null=True),
        ),
    ]
