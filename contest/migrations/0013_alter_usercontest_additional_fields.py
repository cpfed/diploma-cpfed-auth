# Generated by Django 5.1.3 on 2025-01-26 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0012_alter_usercontest_options_contest_image_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercontest',
            name='additional_fields',
            field=models.JSONField(default=dict),
        ),
    ]
