# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0019_auto_20160308_1956'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='format_checklist',
        ),
        migrations.RemoveField(
            model_name='formatchecklist',
            name='date_passed',
        ),
        migrations.AddField(
            model_name='thesis',
            name='format_checklist',
            field=models.ForeignKey(blank=True, to='etd_app.FormatChecklist', null=True),
        ),
    ]
