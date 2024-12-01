# Generated by Django 5.1.3 on 2024-12-01 08:42

import django.core.validators
import re
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_mainuser_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainuser',
            name='handle',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(regex=re.compile('^[a-zA-z_0-9]+$'))], verbose_name='Хэндл'),
        ),
        migrations.AlterField(
            model_name='useractivation',
            name='handle',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(regex=re.compile('^[a-zA-z_0-9]+$'))], verbose_name='Хэндл'),
        ),
    ]
