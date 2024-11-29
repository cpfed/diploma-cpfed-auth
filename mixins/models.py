from django.db import models
from django.utils.translation import gettext_lazy as _


class TimestampMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Время создания"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Время последнего изменения")
    )
