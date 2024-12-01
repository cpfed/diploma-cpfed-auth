import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _

from authentication.forms import UserCreateForm, UserPasswordRecovery, UserLoginForm
from authentication.models import UserActivation, MainUser
from .services.send_email import send_email


# Create your views here.

def user_new(request: HttpResponse):
    error = None
    form = UserCreateForm()
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user_act = UserActivation(**form.cleaned_data)

            # save password safely
            dummy_user = MainUser()
            dummy_user.set_password(user_act.password)
            user_act.password = dummy_user.password
            user_act.save()
            try:
                send_email(email=user_act.email,
                           link=request.build_absolute_uri("/register/" + str(user_act.id)),
                           subject="Активация аккаунта Cpfed",
                           template_name="emails/user_activation.html",
                           username=user_act.handle)
            except Exception as e:
                print("ERROR sending email: ", str(e))
            return render(request, 'result_message.html',
                          {'message': _('На почту отправлено письмо для активации аккаунта')})
        error = str(form.errors)
    return render(request, 'new_user.html', {'error': error, 'form': form, 'form_name': _('Зарегистрироваться')})


def user_activate(request: HttpResponse, token: uuid):
    error = None
    user_act = get_object_or_404(UserActivation, id=token)
    if user_act.is_used:
        error = _("Токен уже использован")
    elif not user_act.is_still_valid:
        error = _("Время жизни токена истекло")
    if error is None:
        user = MainUser(handle=user_act.handle, email=user_act.email, password=user_act.password)
        user.save()
        login(request, user)

        user_act.is_used = True
        user_act.save()

        return redirect(settings.AFTER_LOGIN_URL)
    return render(request, 'result_message.html', {'message': error})


def user_login(request: HttpResponse):
    error = None
    form = UserLoginForm()
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        handle = request.POST['handle']
        password = request.POST['password']
        user = authenticate(request, handle=handle, password=password)
        if user is not None:
            login(request, user)
            return redirect(settings.AFTER_LOGIN_URL)
        form.add_error('password', _('Некорректный хэндл или пароль'))
    return render(request, 'login.html', {'error': error, 'form': form, 'form_name': _('Войти в аккаунт')})


def user_logout(request: HttpResponse):
    # remember current language as logout function drop it
    language = None
    if hasattr(request, 'session'):
        if 'django_language' in request.session:
            language = request.session['django_language']

    logout(request)

    # restore language
    if language:
        request.session['django_language'] = language
    return redirect(settings.LOGOUT_REDIRECT_URL)
