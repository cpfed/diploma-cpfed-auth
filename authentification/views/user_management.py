import uuid

from django.shortcuts import render, redirect
from django.http import HttpResponse, response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _

from authentification.forms import UserCreateForm, UserPasswordRecovery
from authentification.models import UserActivation, MainUser


# Create your views here.

def user_new(request: HttpResponse):
    error = None
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            new_user = UserActivation(**form.cleaned_data)
            new_user.save()
            return render(request, 'result_message.html',
                          {'message': 'На почту отправлено письмо для активации аккаунта'})
        error = str(form.errors)
    return render(request, 'new_user.html', {'error': error})


def user_activate(request: HttpResponse, token: uuid):
    error = None
    try:
        user_act = UserActivation.objects.get(id=token)
    except ObjectDoesNotExist:
        error = _("Запрашиваемая страница не существует")
    else:
        if user_act.is_used:
            error = _("Токен уже использован")
        elif not user_act.is_still_valid:
            error = _("Время жизни токена истекло")
    if error is not None:
        return render(request, 'result_message.html', {'message': error})

    if request.method == 'POST':
        form = UserPasswordRecovery(request.POST)
        if form.is_valid():
            user = MainUser.objects.create_user(handle=user_act.handle, email=user_act.email,
                                                password=form.cleaned_data['new_password'])

            user_act.is_used = True
            user_act.save()
            login(request, user)
            error = None
            return redirect(settings.AFTER_LOGIN_URL)
        error = "Неверные данные"
    return render(request, 'recovery_password.html', {'error': error, 'name': _('Введите пароль для аккаунта')})


def user_login(request: HttpResponse):
    error = None
    if request.method == 'POST':
        handle = request.POST['handle']
        password = request.POST['password']
        user = authenticate(request, handle=handle, password=password)
        if user is not None:
            login(request, user)
            return redirect(settings.AFTER_LOGIN_URL)
        error = "Некорректный хэндл или пароль"
    return render(request, 'login.html', {'error': error})


def user_logout(request: HttpResponse):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)
