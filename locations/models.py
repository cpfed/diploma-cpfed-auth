from django.db import models
from django.utils.translation import gettext_lazy as _
from mixins.models import TimestampMixin


class Region(TimestampMixin):
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=_("Название региона"),
    )

    class Meta:
        verbose_name = _("Регион")
        verbose_name_plural = _("Регионы")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"
