from django.conf import settings
from telegram import Bot

from telegram.request import HTTPXRequest

from .message_cache import MessageCache


request = HTTPXRequest(
    connection_pool_size=16,     # Still increase this, but 16 should be enough for testing
    connect_timeout=20.0,        # Increased connect timeout
    read_timeout=30.0,           # Increased read timeout
    write_timeout=30.0,           # Increased read timeout
    pool_timeout=20.0,           # Increased pool timeout
)


token = settings.TELEGRAM_BOT_TOKEN
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, request=request)
message_cache = MessageCache()
