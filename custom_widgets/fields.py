from django import forms
from django.utils.translation import gettext_lazy as _

from .select_district import SelectDistrictWidget

fields = {
    'SelectDistrictField': forms.CharField(widget=SelectDistrictWidget, label=_('Район'))
}

def get_field(field_name: str, default_label=''):
    return fields.get(field_name, forms.CharField(label=default_label))
