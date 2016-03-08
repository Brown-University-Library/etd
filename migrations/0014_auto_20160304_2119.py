# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0013_auto_20160304_1856'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thesis',
            name='candidate',
        ),
        migrations.AddField(
            model_name='candidate',
            name='thesis',
            field=models.ForeignKey(blank=True, to='etd_app.Thesis', null=True),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='gradschool_checklist',
            field=models.ForeignKey(blank=True, to='etd_app.GradschoolChecklist', null=True),
        ),
    ]
