from django.shortcuts import render, redirect
from django.http import HttpResponse, response
from django.conf import settings
from django.contrib.auth import authenticate, login, logout

from authentification.forms import UserLoginForm, UserCreateForm
from authentification.models import MainUser

# Create your views here.

def user_new(request: HttpResponse):
    error = None
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(settings.AFTER_LOGIN_URL)
        error = str(form.errors)
    return render(request, 'login.html', {'form': UserCreateForm(), 'error': error})


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
    return render(request, 'login.html', {'form': UserLoginForm(), 'error': error})


def user_logout(request: HttpResponse):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)
