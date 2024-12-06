# Generated by Django 5.1.3 on 2024-12-06 10:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата контеста'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contest',
            name='playing_desc',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
