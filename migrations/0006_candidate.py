# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0005_auto_20160216_2023'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_registered', models.DateField(default=datetime.date.today)),
                ('degree', models.ForeignKey(to='etd_app.Degree')),
                ('department', models.ForeignKey(to='etd_app.Department')),
                ('person', models.ForeignKey(to='etd_app.Person')),
                ('year', models.ForeignKey(to='etd_app.Year')),
            ],
        ),
    ]
