# Generated by Django 5.1.3 on 2025-03-20 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0025_contest_text_instead_of_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='telegram_notifications_scheduled',
            field=models.BooleanField(default=False),
        ),
    ]
