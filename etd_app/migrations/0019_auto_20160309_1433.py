# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0018_auto_20160307_2112'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormatChecklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title_page_issue', models.BooleanField(default=False)),
                ('title_page_comment', models.CharField(max_length=190, blank=True)),
                ('signature_page_issue', models.BooleanField(default=False)),
                ('signature_page_comment', models.CharField(max_length=190, blank=True)),
                ('font_issue', models.BooleanField(default=False)),
                ('font_comment', models.CharField(max_length=190, blank=True)),
                ('spacing_issue', models.BooleanField(default=False)),
                ('spacing_comment', models.CharField(max_length=190, blank=True)),
                ('margins_issue', models.BooleanField(default=False)),
                ('margins_comment', models.CharField(max_length=190, blank=True)),
                ('pagination_issue', models.BooleanField(default=False)),
                ('pagination_comment', models.CharField(max_length=190, blank=True)),
                ('format_issue', models.BooleanField(default=False)),
                ('format_comment', models.CharField(max_length=190, blank=True)),
                ('graphs_issue', models.BooleanField(default=False)),
                ('graphs_comment', models.CharField(max_length=190, blank=True)),
                ('dating_issue', models.BooleanField(default=False)),
                ('dating_comment', models.CharField(max_length=190, blank=True)),
                ('general_comments', models.TextField(blank=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='thesis',
            name='format_checklist',
            field=models.ForeignKey(blank=True, to='etd_app.FormatChecklist', null=True),
        ),
    ]
