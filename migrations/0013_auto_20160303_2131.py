# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0012_candidate_embargo_end_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='bursar_receipt',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='dissertation_fee',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='earned_docs_survey',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='gradschool_exit_survey',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='candidate',
            name='pages_submitted_to_gradschool',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
