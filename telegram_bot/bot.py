from django.conf import settings
from telegram import Update

from telegram.ext import Application, CallbackQueryHandler, ContextTypes


token = settings.TELEGRAM_BOT_TOKEN
application = Application.builder().token(token).build()
