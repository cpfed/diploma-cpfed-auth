import uuid

from django.shortcuts import render, redirect
from django.http import HttpResponse, response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from authentication.forms import UserPasswordRecovery, UserPasswordRecoveryRequest
from authentication.models import MainUser, PasswordRecovery
from .services.send_email import send_email


# Create your views here.
def password_recovery_request(request: HttpResponse):
    error = None
    if request.method == 'POST':
        form = UserPasswordRecoveryRequest(request.POST)
        error = "Неверные данные"
        if form.is_valid():
            try:
                user = MainUser.objects.get(**form.cleaned_data)
            except ObjectDoesNotExist:
                error = "Нет пользователя с данной почтой"
            else:
                rec = PasswordRecovery(user=user)
                rec.save()
                send_email(email=user.email,
                           link=request.build_absolute_uri("/passwordRecovery/" + str(rec.id)),
                           subject="Восстановление пароля Cpfed",
                           template_name="emails/recovery_password.html",
                           username=user.handle)
                return render(request, 'result_message.html',
                              {'message': 'Ссылка для восстановления пароля отправлена на почту.'})
    return render(request, 'recovery_password_request.html', {'error': error})


def password_recovery(request: HttpResponse, token: uuid):
    error = None
    try:
        rec = PasswordRecovery.objects.get(id=token)
    except ObjectDoesNotExist:
        error = _("Запрашиваемая страница не существует")
    else:
        if rec.is_used:
            error = _("Токен уже использован")
        elif not rec.is_still_valid:
            error = _("Время жизни токена истекло")
    if error is not None:
        return render(request, 'result_message.html', {'message': error})

    if request.method == 'POST':
        form = UserPasswordRecovery(request.POST)
        if form.is_valid():
            rec.user.set_password(form.cleaned_data['new_password'])
            rec.user.save()

            rec.is_used = True
            rec.save()
            return render(request, 'result_message.html', {'message': _('Пароль успешно изменен!')})
        error = "Неверные данные"
    return render(request, 'recovery_password.html', {'error': error, 'name': _('Введите новый пароль')})
