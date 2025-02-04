from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django import forms
from django.utils.translation import get_language
from django.urls import reverse

from .utils.CustomJSONEncoder import CustomJSONEncoder
# Create your models here.

class Contest(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name=_("Название контеста")
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
    # required_fields = ArrayField(
    #     models.CharField(max_length=100)
    # )
    fields = models.JSONField(
        null=True,
        blank=True
    )
    playing_desc = models.TextField(verbose_name=_("Описание контеста"))
    date = models.DateTimeField(verbose_name=_('Дата контеста'))
    link = models.CharField(max_length=300, verbose_name=_("Ссылка на контест"), blank=True, null=True)
    trial_contest_link = models.CharField(max_length=300, verbose_name="Ссылка на пробный тур", blank=True, null=True)

    show_on_main_page = models.BooleanField(default=True)
    registration_open = models.BooleanField(default=True)
    level_on_main_page = models.IntegerField(default=1)
    image_url = models.CharField(default="capybara.png")
    is_contest = models.BooleanField(default=True)

    text_above_submit_button = models.TextField(null=True, blank=True)
    text_after_submit = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _("Контест")
        verbose_name_plural = _("Контесты")
        ordering = ["id"]

    def __str__(self):
        return f"ID: {self.id}. Контест {self.name}"

    @property
    def remaining_days(self):
        rem = (self.date - timezone.now() + timezone.timedelta(days=0.99999)).days
        return rem

    @property
    def get_link(self):
        return f'{reverse("login")}?contest={self.pk}'

    @property
    def get_trial_link(self):
        return f'{reverse("login")}?contest={self.pk}&trial'

    @property
    def user_fields(self):
        return self.fields.get("user_fields", [])

    @property
    def custom_fields(self):
        return self.fields.get("additional", [])


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
        default=dict,
        encoder=CustomJSONEncoder
    )

    class Meta:
        verbose_name = _("Данные пользователей к контестам")
        verbose_name_plural = _("Данные пользователей к контестам")
        ordering = ["id"]
        models.UniqueConstraint(fields=['user', 'contest'], name='unique_user_registration')

    def __str__(self):
        return f"{self.user} - {self.contest}"

    @property
    def get_full_reg(self) -> dict:
        res = self.additional_fields or dict()
        res.update(self.user.get_user_data_by_fields(self.contest.user_fields))
        return res

    @property
    def get_full_reg_with_additional_data(self) -> dict:
        res = self.get_full_reg
        res.update(self.user.get_user_data_by_fields(['handle', 'first_name', 'last_name']))
        return res


class ContestResult(models.Model):
    user_reg = models.OneToOneField(
        UserContest,
        on_delete=models.CASCADE,
        verbose_name=_("Регистрация"),
        related_name="result"
    )
    rank = models.IntegerField(verbose_name=_("Ранг"))
    points = models.FloatField(verbose_name=_("Очки"), default=0)

    def __str__(self):
        return f"{self.user_reg}: #{self.rank}"
