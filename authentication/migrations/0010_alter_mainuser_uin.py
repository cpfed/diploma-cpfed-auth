# Generated by Django 5.1.3 on 2024-12-03 13:44

import django.core.validators
import re
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_alter_mainuser_phone_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainuser',
            name='uin',
            field=models.CharField(blank=True, max_length=12, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='ИИН может состоять только из 12 цифр', regex=re.compile('^[0-9]{12}$'))], verbose_name='ИИН'),
        ),
    ]
