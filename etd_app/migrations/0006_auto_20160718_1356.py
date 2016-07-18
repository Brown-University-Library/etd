# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0005_degree_degree_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='address_city',
        ),
        migrations.RemoveField(
            model_name='person',
            name='address_state',
        ),
        migrations.RemoveField(
            model_name='person',
            name='address_street',
        ),
        migrations.RemoveField(
            model_name='person',
            name='address_zip',
        ),
        migrations.RemoveField(
            model_name='person',
            name='phone',
        ),
    ]
