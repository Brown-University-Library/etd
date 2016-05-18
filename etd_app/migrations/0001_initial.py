# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_registered', models.DateField(default=datetime.date.today)),
                ('year', models.IntegerField()),
                ('embargo_end_year', models.IntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CommitteeMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(default='reader', max_length=25, choices=[('reader', 'Reader'), ('advisor', 'Advisor')])),
                ('affiliation', models.CharField(max_length=190, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abbreviation', models.CharField(unique=True, max_length=20)),
                ('name', models.CharField(unique=True, max_length=190)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=190)),
                ('bdr_collection_id', models.CharField(max_length=20, unique=True, null=True, blank=True)),
            ],
        ),
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
        migrations.CreateModel(
            name='GradschoolChecklist',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dissertation_fee', models.DateTimeField(null=True, blank=True)),
                ('bursar_receipt', models.DateTimeField(null=True, blank=True)),
                ('gradschool_exit_survey', models.DateTimeField(null=True, blank=True)),
                ('earned_docs_survey', models.DateTimeField(null=True, blank=True)),
                ('pages_submitted_to_gradschool', models.DateTimeField(null=True, blank=True)),
                ('candidate', models.OneToOneField(related_name='gradschool_checklist', to='etd_app.Candidate')),
            ],
        ),
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
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('netid', models.CharField(max_length=100, unique=True, null=True, blank=True)),
                ('orcid', models.CharField(max_length=100, unique=True, null=True, blank=True)),
                ('last_name', models.CharField(max_length=190)),
                ('first_name', models.CharField(max_length=190)),
                ('middle', models.CharField(max_length=100, blank=True)),
                ('email', models.EmailField(max_length=190, unique=True, null=True, blank=True)),
                ('address_street', models.CharField(max_length=190, blank=True)),
                ('address_city', models.CharField(max_length=190, blank=True)),
                ('address_state', models.CharField(max_length=2, blank=True)),
                ('address_zip', models.CharField(max_length=20, blank=True)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
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
                ('num_prelim_pages', models.CharField(max_length=10, blank=True)),
                ('num_body_pages', models.CharField(max_length=10, blank=True)),
                ('status', models.CharField(default='not_submitted', max_length=50, choices=[('not_submitted', 'Not Submitted'), ('pending', 'Awaiting Grad School Review'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])),
                ('date_submitted', models.DateTimeField(null=True, blank=True)),
                ('date_accepted', models.DateTimeField(null=True, blank=True)),
                ('date_rejected', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('candidate', models.OneToOneField(to='etd_app.Candidate')),
                ('keywords', models.ManyToManyField(to='etd_app.Keyword')),
                ('language', models.ForeignKey(blank=True, to='etd_app.Language', null=True)),
            ],
            options={
                'verbose_name_plural': 'Theses',
            },
        ),
        migrations.AddField(
            model_name='formatchecklist',
            name='thesis',
            field=models.OneToOneField(related_name='format_checklist', to='etd_app.Thesis'),
        ),
        migrations.AddField(
            model_name='committeemember',
            name='department',
            field=models.ForeignKey(blank=True, to='etd_app.Department', help_text='Enter either Brown department OR external affiliation.', null=True),
        ),
        migrations.AddField(
            model_name='committeemember',
            name='person',
            field=models.ForeignKey(to='etd_app.Person'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='committee_members',
            field=models.ManyToManyField(to='etd_app.CommitteeMember'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='degree',
            field=models.ForeignKey(to='etd_app.Degree'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='department',
            field=models.ForeignKey(to='etd_app.Department'),
        ),
        migrations.AddField(
            model_name='candidate',
            name='person',
            field=models.ForeignKey(to='etd_app.Person'),
        ),
    ]
