# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0003_auto_20160606_1914'),
    ]

    operations = [
        migrations.RenameField(
            model_name='thesis',
            old_name='file_name',
            new_name='original_file_name',
        ),
    ]
