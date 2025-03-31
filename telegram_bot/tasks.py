# tasks.py
from asgiref.sync import async_to_sync
from celery import shared_task
from datetime import timedelta
from django.utils import timezone

from authentication.models import TelegramUser
from contest.models import Contest
from telegram_bot.services import send_telegram_message


@shared_task
def schedule_contest_notifications():
    print('[doing] schedule_contest_notifications')
    upcoming_contests = Contest.objects.filter(date__gt=timezone.now(), telegram_notifications_scheduled=False)
    print(f'[upcoming_contests] upcoming_contests = {upcoming_contests.count()}')
    for contest in upcoming_contests.iterator():
        day_before = contest.date - timedelta(days=1)
        hour_before = contest.date - timedelta(hours=1)
        fifteen_min_before = contest.date - timedelta(minutes=15)
        now = timezone.now()

        if day_before > now:
            send_contest_notification.apply_async(
                args=[contest.id, "day"],
                eta=day_before
            )

        if hour_before > now:
            send_contest_notification.apply_async(
                args=[contest.id, "hour"],
                eta=hour_before
            )

        if fifteen_min_before > now:
            send_contest_notification.apply_async(
                args=[contest.id, "fifteen_min"],
                eta=fifteen_min_before
            )

        contest.telegram_notifications_scheduled = True
        contest.save()


@shared_task
def send_contest_notification(contest_id, notification_type):
    print('[doing] send_contest_notification')
    try:
        contest = Contest.objects.get(id=contest_id)
        telegram_users = TelegramUser.objects.all()
        messages = {
            "day": f"Reminder: The contest '{contest.name}' will start in 24 hours.",
            "hour": f"Reminder: The contest '{contest.name}' will start in 1 hour.",
            "fifteen_min": f"Reminder: The contest '{contest.name}' will start in 15 minutes."
        }
        print(f'telegram_users = {telegram_users.count()}')

        for telegram_user in telegram_users.iterator():
            message = messages.get(notification_type, "Reminder: You have an upcoming contest!")
            send_message_sync = async_to_sync(send_telegram_message)
            send_message_sync(telegram_user.chat_id, message, max_retries=3)
    except Contest.DoesNotExist:
        print(f"Contest with ID {contest_id} not found")
