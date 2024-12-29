import uuid
import jwt
import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, response, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
import django.utils.datastructures
from django.utils.http import urlencode

from authentication.forms import UserCreateForm, UserPasswordRecovery, UserLoginForm, get_user_form_with_data
from authentication.models import UserActivation, MainUser
from contest.models import Contest
from .services.send_email import send_email_with_context
from utils.cloudflare import check_turnstile_captcha
from utils.funcs import get_next_urlenc
from utils.pixel_events import send_registration


# Create your views here.

def user_new(request: HttpResponse):
    form = UserCreateForm()
    if request.method == 'POST':
        data = {k: request.POST[k] for k in request.POST}
        if 'handle' in data:
            data['handle'] = data['handle'].lower()
        form = UserCreateForm(data)
        if form.is_valid():
            check_turnstile_captcha(request)

            user_act = form.save()

            # save password safely
            dummy_user = MainUser()
            dummy_user.set_password(form.cleaned_data['password'])
            user_act.password = dummy_user.password
            user_act.save()
            send_email_with_context(email=user_act.email,
                                    subject="Активация аккаунта Cpfed",
                                    template_name="emails/user_activation.html",
                                    context={"username": user_act.handle,
                                             "link": request.build_absolute_uri("/register/" + str(user_act.id))
                                                     + get_next_urlenc(request)})
            return render(request, 'result_message.html',
                          {'message': _('На почту отправлено письмо для активации аккаунта')})
    return render(request, 'new_user.html',
                  {'form': form, 'form_name': _('Зарегистрироваться'), 'enable_captcha': not settings.DEBUG})


def _redirect_after_login(request: HttpResponse):
    def get_response():
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        try:
            contest_pk = int(request.GET['contest'])
            link = Contest.objects.get(pk=contest_pk).link
            return redirect(link)
        except (django.utils.datastructures.MultiValueDictKeyError, ValueError, Contest.DoesNotExist):
            pass
        if 'to_esep' in request.GET:
            return redirect('https://esep.cpfed.kz')
        return redirect(settings.AFTER_LOGIN_URL)

    response = get_response()
    jwt_token = jwt.encode({"username": request.user.handle, "email": request.user.email}, settings.JWT_SECRET, algorithm="HS256")
    response.set_cookie(
            max_age=datetime.timedelta(minutes=1),
            key="cpfed_auth",
            value=jwt_token,
            domain=".cpfed.kz",  # Allow cookie sharing across subdomains
            secure=True,  # Use True if HTTPS is enabled
            httponly=True,  # Prevent access via JavaScript
            samesite='None'  # Allow cross-domain cookies
        )
    return response


def user_activate(request: HttpResponse, token: uuid):
    error = None
    user_act = get_object_or_404(UserActivation, id=token)
    if user_act.is_used:
        error = _("Ссылка уже использована")
    elif not user_act.is_still_valid:
        error = _("Ссылка для активации аккаунта устарела")
    if error is None:
        user = MainUser(handle=user_act.handle, email=user_act.email, password=user_act.password)

        send_registration(user.email) # Meta Pixel

        user.save()

        user_act.is_used = True
        user_act.save()

        login(request, user)
        return _redirect_after_login(request)
    return render(request, 'result_message.html', {'message': error})


def user_login(request: HttpResponse):
    if request.user.is_authenticated:
        return _redirect_after_login(request)

    form = UserLoginForm()
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        handle_or_email = request.POST['handle_or_email']
        password = request.POST['password']
        try:
            user = MainUser.objects.get(email=handle_or_email)
            handle = user.handle
        except ObjectDoesNotExist:
            handle = handle_or_email
        handle = handle.lower()
        user = authenticate(request, handle=handle, password=password)
        if user is not None:
            login(request, user)
            return _redirect_after_login(request)
        form.add_error('password', _('Некорректный хэндл/email или пароль'))
    return render(request, 'login.html', {'form': form, 'form_name': _('Войти в аккаунт')})


def user_logout(request: HttpResponse):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


def user_profile(request: HttpResponse):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'profile.html', {'form': get_user_form_with_data(request.user), 'form_name': _('Профиль')})
