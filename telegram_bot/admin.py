from django.contrib import admin
from .models import TelegramMessage


# Register your models here.
@admin.register(TelegramMessage)
class UserContestAdmin(admin.ModelAdmin):
    search_fields = ["code"]
