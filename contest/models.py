from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django import forms

# Create your models here.

class Contest(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
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
    required_fields = ArrayField(
        models.CharField(max_length=100)
    )

    class Meta:
        verbose_name = _("Контест")
        verbose_name_plural = _("Контесты")
        ordering = ["id"]

    def __str__(self):
        return f"ID: {self.id}. Контест {self.name}"

class Championship():
    # date, contests
    pass

class UserContest(models.Model):
    # contest url
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("ID пользователя")
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