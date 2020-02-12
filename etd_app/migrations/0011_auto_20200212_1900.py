# Generated by Django 2.2.10 on 2020-02-12 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('etd_app', '0010_candidate_private_access_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='formatchecklist',
            name='dating_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='font_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='format_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='graphs_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='margins_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='pagination_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='signature_page_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='spacing_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='formatchecklist',
            name='title_page_issue',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
