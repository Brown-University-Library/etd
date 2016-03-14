# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0027_auto_20160314_1422'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thesis',
            name='format_checklist',
        ),
        migrations.AddField(
            model_name='formatchecklist',
            name='thesis',
            field=models.OneToOneField(related_name='format_checklist', default=1, to='etd_app.Thesis'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gradschoolchecklist',
            name='candidate',
            field=models.OneToOneField(related_name='gradschool_checklist', to='etd_app.Candidate'),
        ),
    ]
