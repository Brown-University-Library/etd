# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0002_person_bannerid'),
    ]

    operations = [
        migrations.AddField(
            model_name='thesis',
            name='pid',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='thesis',
            name='status',
            field=models.CharField(default='not_submitted', max_length=50, choices=[('not_submitted', 'Not Submitted'), ('pending', 'Awaiting Grad School Review'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('ingested', 'Ingested'), ('ingest_error', 'Ingestion Error')]),
        ),
    ]
