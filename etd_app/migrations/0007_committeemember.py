# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0006_candidate'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommitteeMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(default='reader', max_length=25, choices=[('reader', 'Reader'), ('director', 'Director')])),
                ('affiliation', models.CharField(max_length=190)),
                ('department', models.ForeignKey(blank=True, to='etd_app.Department', null=True)),
                ('person', models.ForeignKey(to='etd_app.Person')),
            ],
        ),
    ]
