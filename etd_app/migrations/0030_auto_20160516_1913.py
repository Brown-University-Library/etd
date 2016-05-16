# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0029_auto_20160502_1819'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='bdr_collection_id',
            field=models.CharField(default='1', unique=True, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='committeemember',
            name='department',
            field=models.ForeignKey(blank=True, to='etd_app.Department', help_text='Enter either Brown department OR external affiliation.', null=True),
        ),
    ]
