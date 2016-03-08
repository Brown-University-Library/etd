# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0020_auto_20160308_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formatchecklist',
            name='dating_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='dating_issue',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='font_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='font_issue',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='format_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='format_issue',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='general_comments',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='graphs_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='graphs_issue',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='margins_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='margins_issue',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='pagination_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='pagination_issue',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='signature_page_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='signature_page_issue',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='spacing_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='spacing_issue',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='title_page_comment',
            field=models.CharField(max_length=190, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='title_page_issue',
            field=models.NullBooleanField(default=False),
        ),
    ]
