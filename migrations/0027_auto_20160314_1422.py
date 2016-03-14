# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0026_auto_20160314_1338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='gradschool_checklist',
        ),
        migrations.AddField(
            model_name='gradschoolchecklist',
            name='candidate',
            field=models.OneToOneField(default=1, to='etd_app.Candidate'),
            preserve_default=False,
        ),
    ]
