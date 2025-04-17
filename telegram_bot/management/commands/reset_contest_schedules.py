from django.core.management.base import BaseCommand
import asyncio

from telegram import Bot

from django.conf import settings


class Command(BaseCommand):
    help = 'Reset contest schedule notifications'

    def handle(self, *args, **options):
        from telegram_bot.tasks import schedule_contest_notifications
        schedule_contest_notifications()

        self.stdout.write(self.style.SUCCESS('schedule notifications successfully reset'))
