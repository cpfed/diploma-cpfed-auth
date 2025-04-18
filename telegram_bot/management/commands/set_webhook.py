import requests
from django.core.management.base import BaseCommand
import asyncio

from cpfed.settings import TELEGRAM_WEBHOOK_DOMAIN, TELEGRAM_BOT_TOKEN


class Command(BaseCommand):
    help = 'Sets the telegram webhook'

    def handle(self, *args, **options):
        webhook_url = f'{TELEGRAM_WEBHOOK_DOMAIN}/telegram/webhook/{TELEGRAM_BOT_TOKEN}'
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}'
        response = requests.get(url)
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS(f'Webhook set to: {webhook_url}'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to set webhook url: {url}'))

