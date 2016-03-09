# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0022_auto_20160309_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='committee_members',
            field=models.ManyToManyField(to='etd_app.CommitteeMember'),
        ),
    ]
