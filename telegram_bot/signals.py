from django.db.models.signals import post_save

from django.dispatch import receiver
from telegram_bot.models import TelegramMessage


@receiver(post_save, sender=TelegramMessage)
def after_model_save(sender, instance, created, **kwargs):
    from telegram_bot.message_cache import message_cache
    message_cache.refresh()
