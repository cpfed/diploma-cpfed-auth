from django.db import models

from authentication.models import MainUser
from contest.models import Contest
from mixins.models import TimestampMixin

from django.utils.translation import gettext_lazy as _


class TelegramUser(TimestampMixin):
    LANGUAGE = (
        ('kk', 'Қазақша'),
        ('en', 'English'),
        ('ru', 'Русский язык')
    )
    USER_GROUP = (
        (0, _('Школьник')),
        (1, _('Студент')),
        (2, _('Учитель')),
        (3, _('Работник компании'))
    )
    user = models.OneToOneField(
        MainUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Телеграм"),
        related_name="telegram"
    )
    chat_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name="Telegram ID"
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE,
        default=0
    )
    user_group = models.PositiveSmallIntegerField(
        choices=USER_GROUP,
        default=0
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['chat_id'], name='unique_chat_id')
        ]

    def __str__(self):
        return self.user.handle if self.user else self.chat_id


class TelegramMessage(TimestampMixin):
    data = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f'{self.code}: {self.data}'


class ContestNotification(TimestampMixin):
    contest = models.OneToOneField(
        Contest,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="telegram_notification"
    )
    scheduled = models.BooleanField(default=False)

    day_before_sent = models.BooleanField(default=False)
    hour_before_sent = models.BooleanField(default=False)

    day_before_task_id = models.CharField(max_length=255, null=True, blank=True)
    hour_before_task_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.contest:
            return f'{self.contest.name} schedule [24h: {self.day_before_sent}] | [1h: {self.hour_before_sent}]'
        else:
            return f'{self.id}'
