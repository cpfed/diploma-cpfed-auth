import asyncio
import time

from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from django.conf import settings

from asgiref.sync import sync_to_async
from telegram.error import RetryAfter, TimedOut

from authentication.models import MainUser
from .bot import bot
from .utils import LANG_DICT


async def send_telegram_message(chat_id, message, max_retries=3, *args, **kwargs):
    for attempt in range(max_retries):
        try:
            return await bot.send_message(chat_id=chat_id, text=message, **kwargs)
        except RetryAfter as e:
            # Telegram is asking us to slow down
            print(f"Rate limited. Waiting for {e.retry_after} seconds")
            # await asyncio.sleep(e.retry_after)
            time.sleep(e.retry_after)
        except TimedOut:
            # Connection pool timeout, wait a bit
            time.sleep(1)
        except Exception as e:
            time.sleep(1)
    return None  # Failed after max retries


async def send_telegram_photo(chat_id, photo, caption, *args, **kwargs):
    await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, **kwargs)


async def edit_telegram_message(chat_id, message_id, message, *args, **kwargs):
    await bot.edit_message_text(
        text=message,
        chat_id=chat_id,
        message_id=message_id
    )

async def broadcast_telegram_message(users_count, message):
    batch_size = 100

    @sync_to_async
    def get_telegram_users(offset):
        return MainUser.objects.filter(
            telegram_id__isnull=False
        ).values_list('first_name', 'telegram_id')[offset:offset+batch_size]

    for offset in range(0, users_count, batch_size):
        users_with_telegram = await get_telegram_users(offset)
        async for first_name, telegram_id in users_with_telegram:
            await send_telegram_message(telegram_id, message)


async def start(chat_id):
    lang_keyboard = [
        [
            InlineKeyboardButton("Қазақша", callback_data="KAZ"),
            InlineKeyboardButton("Русский", callback_data="RUS"),
        ]
    ]

    lang_reply_markup = InlineKeyboardMarkup(lang_keyboard)

    await send_telegram_message(
        chat_id,
        "Интерфейстің тілін таңдауыңызды сұраймыз.\nПожалуйста, выберите язык интерфейса.",
        reply_markup=lang_reply_markup
    )


async def start_menu(chat_id, language):
    keyboard = [
        [KeyboardButton(LANG_DICT[language]["CONTESTS"])],
        [KeyboardButton(LANG_DICT[language]["COMMUNITY"])],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await send_telegram_message(chat_id, LANG_DICT[language]["CHOOSE_ACTION"], reply_markup=reply_markup)
