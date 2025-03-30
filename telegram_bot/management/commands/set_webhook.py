from django.core.management.base import BaseCommand
import asyncio

from telegram import Bot

from django.conf import settings


class Command(BaseCommand):
    help = 'Sets the telegram webhook'

    def handle(self, *args, **options):
        webhook_url = f'{settings.TELEGRAM_WEBHOOK_DOMAIN}/telegram/webhook/{settings.TELEGRAM_BOT_TOKEN}'

        async def setup_webhook():
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

            # delete existing webhook
            await bot.delete_webhook()
            self.stdout.write(self.style.SUCCESS('Removed existing webhook'))

            # set new webhook
            await bot.set_webhook(url=webhook_url)
            webhook_info = await bot.get_webhook_info()
            self.stdout.write(self.style.SUCCESS(f'Webhook set to: {webhook_info.url}'))

        asyncio.run(setup_webhook())
