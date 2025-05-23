# Generated by Django 5.1.3 on 2025-04-08 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('data', models.CharField(max_length=255)),
                ('data_ru', models.CharField(max_length=255, null=True)),
                ('data_en', models.CharField(max_length=255, null=True)),
                ('data_kk', models.CharField(max_length=255, null=True)),
                ('code', models.CharField(max_length=20, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
