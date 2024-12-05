import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from authentication.forms import UserPasswordRecovery, UserPasswordRecoveryRequest
from authentication.models import MainUser, PasswordRecovery
from .services.send_email import send_email
from utils.cloudflare import check_turnstile_captcha
from utils.funcs import get_next_urlenc


# Create your views here.
def password_recovery_request(request: HttpResponse):
    error = None
    form = UserPasswordRecoveryRequest()
    if request.method == 'POST':
        form = UserPasswordRecoveryRequest(request.POST)
        if form.is_valid():
            check_turnstile_captcha(request)
            try:
                user = MainUser.objects.get(**form.cleaned_data)
            except ObjectDoesNotExist:
                form.add_error('email', _('Указанный для восстановления пароля email не найден'))
            else:
                rec = PasswordRecovery(user=user)
                rec.save()
                try:
                    send_email(email=user.email,
                               link=request.build_absolute_uri(reverse("pass_rec")) + str(rec.id) + get_next_urlenc(request),
                               subject="Восстановление пароля Cpfed",
                               template_name="emails/recovery_password.html",
                               username=user.handle)
                except Exception as e:
                    print("ERROR sending email", str(e))
                return render(request, 'result_message.html',
                              {'message': _('Ссылка для восстановления пароля отправлена на почту.')})
        error = str(form.errors)
    return render(request, 'base_form.html',
                  {'form': form, 'form_name': _('Восстановление пароля'), 'enable_captcha': not settings.DEBUG})

def password_recovery(request: HttpResponse, token: uuid):
    error = None
    rec = get_object_or_404(PasswordRecovery, id=token)
    if rec.is_used:
        error = _("Ссылка уже использована.")
    elif not rec.is_still_valid:
        error = _(
            "Ссылка для восстановления пароля уже устарела. Попробуйте заново.")
    if error is not None:
        return render(request, 'result_message.html', {'message': error})

    form = UserPasswordRecovery()
    if request.method == 'POST':
        form = UserPasswordRecovery(request.POST)
        if form.is_valid():
            rec.user.set_password(form.cleaned_data['password'])
            rec.user.save()

            rec.is_used = True
            rec.save()
            login(request, rec.user)
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return render(request, 'result_message.html', {'message': _('Пароль успешно изменен!')})
        error = str(form.errors)
    return render(request, 'base_form.html', {'form': form, 'form_name': _('Введите новый пароль')})
