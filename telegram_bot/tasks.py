# tasks.py
import time

from celery import shared_task
from datetime import timedelta
from django.utils import timezone

from .models import TelegramUser, ContestNotification
from contest.models import Contest
from telegram_bot.services import send_telegram_message, broadcast_telegram_message
from celery.result import AsyncResult


def schedule_contest(contest: Contest):
    day_before = contest.date - timedelta(days=1)
    hour_before = contest.date - timedelta(hours=1)
    now = timezone.now()

    contest_notification = ContestNotification.objects.get_or_create(contest=contest)[0]
    if contest_notification.scheduled:
        return

    contest_notification.scheduled = True

    if day_before > now:
        contest_notification.day_before_task_id = send_contest_notification.apply_async(
            args=[contest.id, "DAY"],
            eta=day_before
        )

    if hour_before > now:
        contest_notification.hour_before_task_id = send_contest_notification.apply_async(
            args=[contest.id, "HOUR"],
            eta=hour_before
        )

    contest_notification.save()


def remove_contest_schedule(contest: Contest):
    try:
        contest_notification = ContestNotification.objects.get(contest=contest)
        if contest_notification.day_before_task_id:
            AsyncResult(contest_notification.day_before_task_id).revoke(terminate=False)

        if contest_notification.hour_before_task_id:
            AsyncResult(contest_notification.hour_before_task_id).revoke(terminate=False)

        contest_notification.day_before_task_id = None
        contest_notification.hour_before_task_id = None
        contest_notification.scheduled = False
        contest_notification.save()

    except ContestNotification.DoesNotExist:
        pass


def schedule_contest_notifications():
    upcoming_contests = Contest.objects.filter(date__gt=timezone.now())
    for contest in upcoming_contests.iterator():
        remove_contest_schedule(contest)
        schedule_contest(contest)


@shared_task
def send_contest_notification(contest_id, notification_type):
    try:
        from telegram_bot.message_cache import message_cache

        contest = Contest.objects.get(id=contest_id)
        telegram_users = TelegramUser.objects.filter(user__isnull=False).values_list('user__first_name', 'chat_id', 'language')
        telegram_users_count = telegram_users.count()

        batch_size = 30
        notification_code = f'CONTEST_IN_{notification_type}'

        if notification_type == 'DAY':
            contest.telegram_notification.day_before_sent = True
            contest.telegram_notification.save()
        else:
            contest.telegram_notification.hour_before_sent = True
            contest.telegram_notification.save()

        for offset in range(0, telegram_users_count, batch_size):
            batch = telegram_users[offset: offset+batch_size]
            for first_name, chat_id, language in batch:
                message = message_cache.get_message(language, notification_code).format(contest.name, contest.link)
                send_telegram_message(chat_id, message, reply_markup=None, parse_mode='MarkdownV2')

            # https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this
            time.sleep(2)

    except Contest.DoesNotExist:
        print(f"Contest with ID {contest_id} not found")
