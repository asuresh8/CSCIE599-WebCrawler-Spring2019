# Generated by Django 2.1.7 on 2019-03-25 16:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main_app', '0004_auto_20190325_1207'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('s3_bucket', models.URLField(blank=True, default='', max_length=500)),
                ('api_key', models.CharField(max_length=512)),
                ('api_secret', models.CharField(max_length=512)),
                ('num_crawlers', models.PositiveIntegerField(default=1)),
                ('created', models.DateTimeField(editable=False, verbose_name='crawl request creation time')),
                ('modified', models.DateTimeField(verbose_name='crawl request modification time')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
