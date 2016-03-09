# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0023_candidate_committee_members'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committeemember',
            name='role',
            field=models.CharField(default='reader', max_length=25, choices=[('reader', 'Reader'), ('advisor', 'Advisor')]),
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
    ]
