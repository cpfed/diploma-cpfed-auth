from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from .models import UserActivation, MainUser


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль', validators=[validate_password])

    class Meta:
        model = UserActivation
        fields = ('handle', 'email', 'password')


class UserLoginForm(forms.Form):
    handle = forms.CharField(label='Хэндл')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class UserPasswordRecoveryRequest(forms.Form):
    email = forms.EmailField()


class UserPasswordRecovery(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(), label='Пароль', validators=[validate_password])
