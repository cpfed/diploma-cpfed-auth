from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language

from .select_district import SelectDistrictWidget

fields = {
    'SelectDistrictField': forms.CharField(widget=SelectDistrictWidget, label=_('Район'))
}

def get_field(field):
    label = field['name']

    if get_language() == 'en' and 'name_en' in field: label = field.get('name_en', label)
    elif get_language() == 'kk' and 'name_kk' in field: label = field['name_kk']
    elif 'name_ru' in field: label = field['name_ru']

    return fields.get(field.get('field', ''), forms.CharField(label=label))
