# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0009_auto_20160225_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 25, 21, 19, 42, 295315, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='candidate',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 25, 21, 19, 52, 294603, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='committeemember',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 25, 21, 20, 3, 766464, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='committeemember',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 25, 21, 20, 8, 134248, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 25, 21, 20, 13, 518307, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='person',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 25, 21, 20, 18, 86093, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='thesis',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 25, 21, 20, 23, 406083, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='thesis',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 25, 21, 20, 27, 606063, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
