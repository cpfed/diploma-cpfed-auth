# Generated by Django 5.1.3 on 2025-01-13 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0006_contestresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='show_on_main_page',
            field=models.BooleanField(default=True),
        ),
    ]
