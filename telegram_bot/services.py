import asyncio
from telegram import Bot

from django.conf import settings


async def send_telegram_message(telegram_id, message, *args, **kwargs):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=telegram_id, text=message, **kwargs)


async def send_telegram_photo(telegram_id, photo, caption, *args, **kwargs):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    await bot.send_photo(chat_id=telegram_id, photo=photo, caption=caption, **kwargs)
