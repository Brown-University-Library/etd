# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0008_keyword_language_thesis'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='thesis',
            options={'verbose_name_plural': 'Theses'},
        ),
        migrations.AlterField(
            model_name='committeemember',
            name='affiliation',
            field=models.CharField(max_length=190, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='address_city',
            field=models.CharField(max_length=190, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='address_state',
            field=models.CharField(max_length=2, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='address_street',
            field=models.CharField(max_length=190, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='address_zip',
            field=models.CharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='middle',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
