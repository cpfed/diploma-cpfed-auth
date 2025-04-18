# Generated by Django 5.1.3 on 2024-12-06 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0002_contest_date_contest_playing_desc'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='name_en',
            field=models.CharField(default='', max_length=128, verbose_name='Название контестаen'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contest',
            name='name_kk',
            field=models.CharField(default='', max_length=128, verbose_name='Название контестаkk'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contest',
            name='playing_desc_en',
            field=models.TextField(default='', verbose_name='Описание контеста: en'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contest',
            name='playing_desc_kk',
            field=models.TextField(default='', verbose_name='Описание контеста: kk'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='contest',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Название контестаru'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='playing_desc',
            field=models.TextField(verbose_name='Описание контеста: ru'),
        ),
    ]
