# Generated by Django 5.1.3 on 2025-03-18 20:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0014_mainuser_is_offline_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mainuser',
            name='is_offline',
        ),
        migrations.AlterField(
            model_name='onsitelogin',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='onsite_login', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
