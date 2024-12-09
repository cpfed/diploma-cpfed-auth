import uuid
import re

from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import ValidationError, RegexValidator

from phonenumber_field.modelfields import PhoneNumberField

from utils import constants
from mixins.models import TimestampMixin
from locations.models import Region

handle_validator = RegexValidator(regex=re.compile(r'^[a-zA-z_0-9]+$'),
                                  message=_('Хэндл может состоять только из латинских букв, цифр и _'))
uin_validator = RegexValidator(regex=re.compile(r'^[0-9]{12}$'), message=_('ИИН может состоять только из 12 цифр'))


class MainUserManager(BaseUserManager):
    DELETE_FIELD = "is_deleted"

    def create_user(self, handle, email, password):
        """
        Creates and saves a user with the given handle and password
        """
        if email is None:
            raise TypeError("Users must have an email address.")
        user = self.model(email=self.normalize_email(email), handle=handle, password=password)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, handle, email, password):
        """
        Creates and saves a superuser with the given email and password
        """
        if password is None:
            raise TypeError("Superusers must have a password.")
        user = self.create_user(handle, email, password)
        user.is_admin = True
        user.is_superuser = True
        user.is_moderator = True
        user.save()
        return user


class MainUser(AbstractBaseUser, PermissionsMixin, TimestampMixin):
    handle = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Хэндл"),
        validators=[handle_validator]
    )
    email = models.EmailField(
        max_length=100,
        unique=True,
        verbose_name=_("Электронная почта")
    )
    first_name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_("Имя")
    )
    last_name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_("Фамилия")
    )
    phone_number = PhoneNumberField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Телефонный номер")
    )
    gender = models.CharField(
        max_length=20,
        choices=constants.GENDER,
        blank=True,
        null=True,
        verbose_name=_("Пол")
    )
    uin = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("ИИН"),
        validators=[uin_validator]
    )
    t_shirt_size = models.CharField(
        choices=constants.T_SHIRT_SIZES,
        max_length=5,
        blank=True,
        null=True,
        verbose_name=_("Размер футболки")
    )
    employment_status = models.CharField(
        choices=constants.EMPLOYMENT_STATUS,
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_("Статус занятости")
    )
    place_of_study_of_work = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_("Место учебы или работы")
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Регион")
    )
    citizen_of_kz = models.BooleanField(
        verbose_name=_("Гражданин РК?"),
        default=True
    )

    is_admin = models.BooleanField(verbose_name=_("Админ?"), default=False)
    is_moderator = models.BooleanField(verbose_name=_("Модератор?"), default=False)
    is_deleted = models.BooleanField(verbose_name=_("Аккаунт удален?"), default=False)
    is_active = models.BooleanField(verbose_name=_("Аккаунт активен?"), default=True)

    objects = MainUserManager()

    USERNAME_FIELD = "handle"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ["id"]

    def __str__(self):
        return f"{self.id}, {self.handle if self.handle else f'{self.first_name} {self.last_name}'}"

    @property
    def is_staff(self):
        return self.is_admin or self.is_moderator

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        super().clean()
        if self.employment_status != constants.EMPLOYMENT_STATUS[2][0] and self.place_of_study_of_work is None:
            raise ValidationError({'place_of_study_of_work': _('Поле не может быть пустым')})

    @property
    def get_fields(self):
        return {f.name for f in self._meta.get_fields()}

    def get_user_data_by_fields(self, need_fields):
        if 'password' in need_fields:
            raise Exception('Нельзя экспортировать пароль')
        return {f: getattr(self, f) for f in self.get_fields if f in need_fields}


def _password_default_exp_date():
    return timezone.now() + timezone.timedelta(minutes=30)


class PasswordRecovery(TimestampMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        MainUser,
        on_delete=models.DO_NOTHING,
        null=True,
        verbose_name=_("Пользователь")
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name=_("Ссылка использована?")
    )
    expiration_date = models.DateTimeField(
        default=_password_default_exp_date,
        verbose_name=_('Срок годности')
    )

    @property
    def is_still_valid(self):
        return not self.is_used and self.expiration_date > timezone.now()

    def __str__(self):
        return f"Ссылка {self.id} для {self.user.handle} {'еще активна' if self.is_still_valid else ('использована' if self.is_used else 'не была использована')}"

    class Meta:
        verbose_name = _("Восстановление пароля")
        verbose_name_plural = _("Восстановление пароля")
        ordering = ["-expiration_date"]


class UserActivation(TimestampMixin):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    handle = models.CharField(
        max_length=100,
        verbose_name=_("Хэндл"),
        validators=[handle_validator]
    )
    email = models.EmailField(
        max_length=100,
        verbose_name=_("Электронная почта")
    )
    password = models.CharField(
        max_length=128,
        verbose_name=_("Пароль")
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name=_("Ссылка использована?")
    )
    expiration_date = models.DateTimeField(
        default=_password_default_exp_date,
        verbose_name=_('Срок годности')
    )

    @property
    def is_still_valid(self):
        return not self.is_used and self.expiration_date > timezone.now()

    def _check_unique_email_or_handle(self, **kwargs):
        if MainUser.objects.filter(**kwargs).exists():
            return True
        # check UserActivation for active links
        qs = UserActivation.objects.filter(**kwargs, expiration_date__gt=timezone.now(), is_used=False)
        if self.pk is not None:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            return True
        return False

    def validate_unique(self, *args, **kwargs):
        super().validate_unique(*args, **kwargs)
        if self._check_unique_email_or_handle(handle=self.handle):
            raise ValidationError({'handle': _('Хэндл уже занят')})

        if self._check_unique_email_or_handle(email=self.email):
            raise ValidationError({'email': _('Email уже занят')})

    def __str__(self):
        return f"Ссылка {self.id} для {self.handle} {'еще активна' if self.is_still_valid else ('использована' if self.is_used else 'не была использована')}"

    class Meta:
        verbose_name = _("Активация аккаунта")
        verbose_name_plural = _("Активация аккаунта")
        ordering = ["-expiration_date"]
