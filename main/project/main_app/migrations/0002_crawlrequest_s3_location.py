# Generated by Django 2.1.7 on 2019-03-24 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlrequest',
            name='s3_location',
            field=models.URLField(blank=True, default='', max_length=500),
        ),
    ]
