import uuid

from django.shortcuts import render, redirect
from django.http import HttpResponse, response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import ObjectDoesNotExist
from django.utils import timezone

from authentification.forms import UserPasswordRecovery, UserPasswordRecoveryRequest
from authentification.models import MainUser, PasswordRecovery


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
                print(str(rec.id))
                return render(request, 'recovery_password_request_successful.html')
    return render(request, 'recovery_password_request.html', {'error': error})


def password_recovery(request: HttpResponse, token: uuid):
    error = None
    try:
        rec = PasswordRecovery.objects.get(id=token)
    except ObjectDoesNotExist:
        error = "Запрашиваемая страница не существует"
    else:
        if rec.is_used:
            error = "Токен уже использован"
        elif rec.expiration_date < timezone.now():
            error = "Время жизни токена истекло"
    if error is not None:
        return render(request, 'password_recovery_result.html', {'error': error})

    if request.method == 'POST':
        form = UserPasswordRecovery(request.POST)
        if form.is_valid():
            rec.user.set_password(form.cleaned_data['new_password'])
            rec.user.save()

            rec.is_used = True
            rec.save()
            error = None
            return render(request, 'recovery_password_result.html', {'error': error, 'ok': True})
        error = "Неверные данные"
    return render(request, 'recovery_password.html', {'error': error})
