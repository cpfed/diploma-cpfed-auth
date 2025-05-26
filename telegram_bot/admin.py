from django.contrib import admin
from .models import TelegramUser, TelegramMessage, ContestNotification, TelegramQA


# Register your models here.
@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    search_fields = ["code"]


@admin.register(ContestNotification)
class ContestNotificationAdmin(admin.ModelAdmin):
    search_fields = ["contest"]


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    search_fields = ["user"]


@admin.register(TelegramQA)
class TelegramQAAdmin(admin.ModelAdmin):
    search_fields = ["telegram_user"]
