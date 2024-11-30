from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import fields_for_model


from .models import Contest


class ContestRegistrationForm(forms.Form):
    def __init__(self, contest: Contest, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        req_fields = contest.required_fields
        # list of available fields in user model
        user_fields = fields_for_model(get_user_model())
        for field in req_fields:
            self.fields[field] = forms.CharField()
            if (user is not None) and field in user_fields:
                self.fields[field] = user_fields[field]
                self.initial[field] = getattr(user, field)
