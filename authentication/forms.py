from django import forms
from .models import UserActivation, MainUser


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    class Meta:
        model = UserActivation
        fields = ('handle', 'email', 'password')

class UserLoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    class Meta:
        model = MainUser
        fields = ('handle', 'password')
        labels = {'password': 'Пароль'}


class UserPasswordRecoveryRequest(forms.Form):
    email = forms.EmailField()


class UserPasswordRecovery(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(), label='Пароль')
