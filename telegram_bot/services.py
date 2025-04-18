import time

import requests

from cpfed.settings import TELEGRAM_BOT_TOKEN

from .models import TelegramUser
from telegram_bot.message_cache import message_cache


def send_telegram_message(chat_id, message, reply_markup=None, parse_mode=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    if reply_markup:
        payload.update({
            "reply_markup": reply_markup
        })

    if parse_mode:
        payload.update({
            "parse_mode": parse_mode
        })
    response = requests.post(url=url, json=payload)
    return response.status_code


def send_telegram_photo(chat_id, photo, caption, *args, **kwargs):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo,
        "caption": caption
    }
    response = requests.post(url=url, json=payload)
    return response.status_code


def edit_telegram_message(chat_id, message_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessage"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": message,
        "reply_markup": None
    }
    response = requests.post(url=url, json=payload)
    return response.status_code


def broadcast_telegram_message(telegram_users_count, message):
    batch_size = 30
    telegram_users = TelegramUser.objects.filter(user__isnull=False).values_list('user__first_name', 'chat_id')
    for offset in range(0, telegram_users_count, batch_size):
        batch = telegram_users[offset: offset+batch_size]
        for first_name, chat_id in batch:
            send_telegram_message(chat_id, message)

        # https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this
        time.sleep(2)


def start(chat_id):
    lang_keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "Қазақша",
                    "callback_data": "kk"
                }
            ],
            [
                {
                    "text": "Русский",
                    "callback_data": "ru"
                }
            ]
        ]
    }

    send_telegram_message(
        chat_id,
        "Интерфейстің тілін таңдауыңызды сұраймыз.\nПожалуйста, выберите язык интерфейса.",
        reply_markup=lang_keyboard
    )


def start_menu(chat_id, language):
    keyboard = {
        "keyboard": [
            [
                {
                    "text": message_cache.get_message(language, "CONTESTS")
                }
            ],
            [
                {
                    "text":  message_cache.get_message(language, "COMMUNITY")
                }
            ],
            [
                {
                    "text": message_cache.get_message(language, "WEB_APP"),
                    "web_app": {
                        "url": "https://auth.cpfed.kz/"
                    }
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    send_telegram_message(chat_id, message_cache.get_message(language, "CHOOSE_ACTION"), keyboard)
