# Generated by Django 3.2.12 on 2022-07-04 09:51

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FeedSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='Torrent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('pub_date', models.DateTimeField()),
                ('link', models.URLField()),
                ('guid', models.URLField()),
                ('enclosure_type', models.CharField(max_length=255)),
                ('enclosure_length', models.PositiveBigIntegerField()),
                ('enclosure_url', models.URLField(validators=[django.core.validators.URLValidator(schemes=['http', 'https', 'ftp', 'ftps', 'magnet'])])),
                ('added', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FeedMatcher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matcher', models.CharField(max_length=255)),
                ('download_dir', models.CharField(max_length=255)),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transrss_manager.feedsource')),
            ],
        ),
    ]
