from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from django.forms.widgets import Widget, Select
from phonenumber_field.formfields import PhoneNumberField

from .select_district import SelectDistrictWidget

grades_choice = (
    ('7 класс', _('7 класс')),
    ('8 класс', _('8 класс')),
    ('Другое', _('Другое'))
)
lang_choice = (
    ('Қазақша', 'Қазақша'),
    ('Русский', 'Русский'),
    ('Другое', _('Другое'))
)
work_type_choice = (
    ('фриланс', _('Фриланс')),
    ('офис', _('Работаю в офисе'))
)


class DateInput(forms.widgets.DateInput):
    input_type = 'date'


fields = {
    'SelectDistrictField': forms.CharField(widget=SelectDistrictWidget, label=_('Район')),
    'SelectGradeField': forms.ChoiceField(choices=grades_choice, label=_('Класс обучения')),
    'SelectEduLangField': forms.ChoiceField(choices=lang_choice, label=_('Язык обучения')),
    'WorkTypeField': forms.ChoiceField(choices=work_type_choice, label=_('Формат работы')),
    'ParentPhoneNumberField': PhoneNumberField(label=_('Телефон одного из родителей ')),
    'BirthDateField': forms.DateField(widget=DateInput(), label=_('Дата рождения')),
}


def get_field(field):
    label = field['name']

    if get_language() == 'en' and 'name_en' in field:
        label = field.get('name_en', label)
    elif get_language() == 'kk' and 'name_kk' in field:
        label = field['name_kk']
    elif 'name_ru' in field:
        label = field['name_ru']

    res = fields.get(field.get('field', ''), forms.CharField(label=label))

    if "not_required" in field:
        res.required = False

    return res
