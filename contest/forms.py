from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import fields_for_model
from django.utils.translation import gettext_lazy as _

from .models import Contest
from custom_widgets.fields import get_field


class ContestRegistrationForm(forms.Form):
    def __init__(self, contest: Contest, user=None, user_reg=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # list of available fields in user model
        user_fields = fields_for_model(get_user_model())
        for field in contest.user_fields:
            self.fields[field] = user_fields[field]
            if field != 'place_of_study_of_work':  # require will be checked on server side
                self.fields[field].required = True
                self.fields[field].widget.attrs['required'] = 'required'
            if (user is not None):
                self.initial[field] = getattr(user, field)

        for field in contest.custom_fields:
            name = field['name']
            self.fields[name] = get_field(field)
            if user_reg is not None and user_reg.additional_fields is not None:
                self.initial[name] = user_reg.additional_fields.get(name, None)

class AdminTextAreaWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        attrs = kwargs.setdefault('attrs', {})
        attrs.setdefault('cols', 60)
        attrs.setdefault('rows', 1)
        super().__init__(*args, **kwargs)
