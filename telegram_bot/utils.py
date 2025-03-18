from django.core.exceptions import ObjectDoesNotExist

from .services import send_notification
from authentication.models import MainUser

from django.conf import settings

from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler

import os


def notify_user(handle, message):
    try:
        user = MainUser.objects.get(handle=handle, is_active=True)
        send_notification(user.telegram_id, message)
        return True
    except ObjectDoesNotExist:
        return False


def notify_all_users(message):
    profiles = MainUser.objects.filter(telegram_id__isnull=False, is_active=True)
    for profile in profiles:
        send_notification(profile.telegram_chat_id, message)
    return len(profiles)
