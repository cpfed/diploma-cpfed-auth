from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import fields_for_model
from django.utils.translation import gettext_lazy as _

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
                if field != 'place_of_study_of_work':  # require will be checked on server side
                    self.fields[field].required = True
                self.initial[field] = getattr(user, field)

    def clean(self):
        cleaned_data = super().clean()
        if 'place_of_study_of_work' in cleaned_data and 'employment_status' in cleaned_data and cleaned_data.get(
                'place_of_study_of_work') == '':
            self.add_error('place_of_study_of_work', _('Поле не может быть пустым'))
        return cleaned_data
