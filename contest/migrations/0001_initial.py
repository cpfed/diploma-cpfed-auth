# Generated by Django 5.1.3 on 2024-11-30 06:04

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Название контеста')),
                ('required_fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None)),
            ],
            options={
                'verbose_name': 'Контест',
                'verbose_name_plural': 'Контесты',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='UserContest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional_fields', models.JSONField(null=True)),
                ('contest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contest.contest', verbose_name='ID контеста')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ID пользователя')),
            ],
            options={
                'verbose_name': 'Данные пользователей к контестам',
                'verbose_name_plural': 'Данные пользователей к контестам',
                'ordering': ['user__id'],
            },
        ),
    ]
