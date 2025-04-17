from django.db.models.signals import pre_save, post_save, pre_delete

from django.dispatch import receiver
from .models import Contest


@receiver(pre_save, sender=Contest)
def before_model_save(sender, instance, **kwargs):
    if instance.pk:
        original_contest = Contest.objects.get(pk=instance.pk)
        if original_contest.date != instance.date:
            from telegram_bot.tasks import schedule_contest, remove_contest_schedule

            remove_contest_schedule(original_contest)
            schedule_contest(instance)


@receiver(post_save, sender=Contest)
def after_model_save(sender, instance, created, **kwargs):
    if created:
        from telegram_bot.tasks import schedule_contest
        schedule_contest(instance)


@receiver(pre_delete, sender=Contest)
def before_model_delete(sender, instance, **kwargs):
    from telegram_bot.tasks import remove_contest_schedule
    remove_contest_schedule(instance)
