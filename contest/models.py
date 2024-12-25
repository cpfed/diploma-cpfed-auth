from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django import forms
from django.utils.translation import get_language


# Create your models here.

class Contest(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name=_("Название контеста") + ' ru'
    )
    name_kk = models.CharField(
        max_length=128,
        verbose_name=_("Название контеста") + ' kk'
    )
    name_en = models.CharField(
        max_length=128,
        verbose_name=_("Название контеста") + ' en'
    )
    # next_contest = models.ForeignKey(
    #     "self",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="next_contest_id+",
    #     default=None,
    #     verbose_name=_("ID следующего контеста")
    # )
    # is_active = models.BooleanField(
    #     verbose_name=_("Контест активен?"),
    #     default=True,
    # )
    required_fields = ArrayField(
        models.CharField(max_length=100)
    )
    playing_desc = models.TextField(
        verbose_name=_("Описание контеста: ") + 'ru'
    )
    playing_desc_kk = models.TextField(
        verbose_name=_("Описание контеста: ") + 'kk'
    )
    playing_desc_en = models.TextField(
        verbose_name=_("Описание контеста: ") + 'en'
    )

    date = models.DateTimeField(
        verbose_name=_('Дата контеста')
    )

    class Meta:
        verbose_name = _("Контест")
        verbose_name_plural = _("Контесты")
        ordering = ["id"]

    def __str__(self):
        return f"ID: {self.id}. Контест {self.name}"

    @property
    def remaining_days(self):
        return (self.date - timezone.now()).days

    @property
    def get_name(self):
        match get_language():
            case 'en':
                return self.name_en
            case 'kk':
                return self.name_kk
            case _:
                return self.name

    @property
    def get_desc(self):
        match get_language():
            case 'en':
                return self.playing_desc_en
            case 'kk':
                return self.playing_desc_kk
            case _:
                return self.playing_desc


class Championship():
    # date, contests
    pass


class UserContest(models.Model):
    # contest url
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("ID пользователя"),
        related_name="contests"
    )
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        verbose_name=_("ID контеста")
    )
    additional_fields = models.JSONField(
        null=True
    )

    class Meta:
        verbose_name = _("Данные пользователей к контестам")
        verbose_name_plural = _("Данные пользователей к контестам")
        ordering = ["user__id"]
        models.UniqueConstraint(fields=['user', 'contest'], name='unique_user_registration')

    def __str__(self):
        return f"{self.user} - {self.contest}"

    @property
    def get_full_reg(self) -> dict:
        res = self.additional_fields
        res.update(self.user.get_user_data_by_fields(self.contest.required_fields))
        return res