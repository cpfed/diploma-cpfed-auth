from django import forms
from authentification.models import UserActivation


class UserCreateForm(forms.ModelForm):
    class Meta:
        model = UserActivation
        fields = ('handle', 'email')


class UserPasswordRecoveryRequest(forms.Form):
    email = forms.EmailField()


class UserPasswordRecovery(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput())
