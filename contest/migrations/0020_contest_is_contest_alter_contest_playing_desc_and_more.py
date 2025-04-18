# Generated by Django 5.1.3 on 2025-02-04 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0019_contest_text_after_submit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='is_contest',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='contest',
            name='playing_desc',
            field=models.TextField(verbose_name='Описание контеста'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='playing_desc_en',
            field=models.TextField(null=True, verbose_name='Описание контеста'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='playing_desc_kk',
            field=models.TextField(null=True, verbose_name='Описание контеста'),
        ),
        migrations.AlterField(
            model_name='contest',
            name='playing_desc_ru',
            field=models.TextField(null=True, verbose_name='Описание контеста'),
        ),
    ]
