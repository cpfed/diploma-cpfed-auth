# Generated by Django 5.1.3 on 2025-03-20 07:39

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0011_alter_mainuser_handle_alter_useractivation_handle'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainuser',
            name='telegram_token',
            field=models.CharField(default=uuid.uuid4, max_length=128, verbose_name='Telegram TOKEN'),
        ),
        migrations.AlterField(
            model_name='mainuser',
            name='t_shirt_size',
            field=models.CharField(blank=True, choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')], max_length=5, null=True, verbose_name='Размер футболки'),
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Время последнего изменения')),
                ('chat_id', models.CharField(blank=True, max_length=128, null=True, verbose_name='Telegram ID')),
                ('language', models.PositiveSmallIntegerField(choices=[(0, 'Қазақша'), (1, 'Русский язык')], default=0)),
                ('user_group', models.PositiveSmallIntegerField(choices=[(0, 'Школьник'), (1, 'Студент'), (2, 'Учитель'), (3, 'Работник компании')], default=0)),
                ('telegram', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='telegram', to=settings.AUTH_USER_MODEL, verbose_name='Телеграм')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('chat_id',), name='unique_chat_id')],
            },
        ),
    ]
