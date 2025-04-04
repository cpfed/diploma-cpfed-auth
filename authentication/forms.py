from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from .models import UserActivation, MainUser


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль', validators=[validate_password])
    password1 = forms.CharField(widget=forms.PasswordInput, label='Подтвердите пароль')

    class Meta:
        model = UserActivation
        fields = ('handle', 'email', 'password')

    def clean(self):
        super().clean()
        if self.cleaned_data.get('password', '') != self.cleaned_data.get('password1', None):
            self.add_error('password1', _('Пароли не совпадают'))


class UserLoginForm(forms.Form):
    handle_or_email = forms.CharField(label=_('Хэндл/Email'))
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class UserPasswordRecoveryRequest(forms.Form):
    email = forms.EmailField(label=_('Электронная почта'))


class UserPasswordRecovery(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label='Пароль', validators=[validate_password])
    password1 = forms.CharField(widget=forms.PasswordInput, label=_('Подтвердите пароль'))

    def clean(self):
        super().clean()
        if self.cleaned_data.get('password', '') != self.cleaned_data.get('password1', None):
            self.add_error('password1', _('Пароли не совпадают'))


def get_user_form(req_fields: list[str]):
    # if any(f in req_fields for f in ('handle', 'email', 'password')): # TODO
    #     raise Exception('Хэндл, email или пароль не могут быть в форме регистрации')
    user_fields = {x.name for x in MainUser._meta.get_fields()}

    class UserForm(forms.ModelForm):
        class Meta:
            model = MainUser
            fields = tuple(f for f in req_fields if f in user_fields)

    return UserForm


# UserFullForm = get_user_form(
#     ['handle', 'email', 'first_name', 'last_name', 'phone_number', 'uin', 't_shirt_size', 'employment_status',
#      'place_of_study_of_work', 'region', 'telegram_id', 'telegram_token'])


def get_user_form_with_data(user: MainUser):
    fields_to_include = ['handle', 'email', 'first_name', 'last_name', 'phone_number', 'uin', 't_shirt_size', 'employment_status',
                         'place_of_study_of_work', 'region']
    UserFullForm = get_user_form(fields_to_include)

    data = dict()
    for f in UserFullForm().fields:
        data[f] = getattr(user, f)
    return UserFullForm(data)