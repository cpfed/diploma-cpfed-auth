from django.db.models.signals import pre_save, post_save, pre_delete

from django.dispatch import receiver
from .models import Contest
from telegram_bot.tasks import schedule_contest, remove_contest_schedule


@receiver(pre_save, sender=Contest)
def before_model_save(sender, instance, **kwargs):
    if instance.pk:
        print('model updated ', instance.name)
        original_contest = Contest.objects.get(pk=instance.pk)
        print('original name = ', original_contest.name)
        if original_contest.date != instance.date:
            print('dates changed')
            remove_contest_schedule(original_contest)
            print('removed contest schedule', original_contest.date)
            schedule_contest(instance)
            print('scheduled new time', instance.date)


@receiver(post_save, sender=Contest)
def after_model_save(sender, instance, created, **kwargs):
    if created:
        print('model saved [created] ', instance.name)
        schedule_contest(instance)
        print('scheduled contest notifications [created] ', instance.name)


@receiver(pre_delete, sender=Contest)
def before_model_delete(sender, instance, **kwargs):
    remove_contest_schedule(instance)
