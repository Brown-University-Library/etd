# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0020_auto_20160309_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thesis',
            name='status',
            field=models.CharField(default=b'not_submitted', max_length=50, choices=[(b'not_submitted', b'Not Submitted'), (b'pending', b'Awaiting Grad School Review'), (b'accepted', b'Accepted'), (b'rejected', b'Rejected')]),
        ),
    ]
