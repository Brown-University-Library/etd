# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0019_auto_20160309_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thesis',
            name='status',
            field=models.CharField(default=b'not_submitted', max_length=50, choices=[(b'not_submitted', b'Not Submitted'), (b'pending', b'Awaiting Grad School Action'), (b'accepted', b'Accepted'), (b'rejected', b'Rejected')]),
        ),
    ]
