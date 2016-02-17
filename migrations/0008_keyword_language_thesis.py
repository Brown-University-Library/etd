# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0007_committeemember'),
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(unique=True, max_length=190)),
                ('search_text', models.CharField(max_length=190, blank=True)),
                ('authority', models.CharField(max_length=100, blank=True)),
                ('authority_uri', models.CharField(max_length=190, blank=True)),
                ('value_uri', models.CharField(max_length=190, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Thesis',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('document', models.FileField(upload_to=b'')),
                ('file_name', models.CharField(max_length=190)),
                ('checksum', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('abstract', models.TextField()),
                ('status', models.CharField(max_length=50)),
                ('candidate', models.ForeignKey(to='etd_app.Candidate')),
                ('keywords', models.ManyToManyField(to='etd_app.Keyword')),
                ('language', models.ForeignKey(to='etd_app.Language', null=True)),
            ],
        ),
    ]
