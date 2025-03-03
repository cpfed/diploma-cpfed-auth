import copy

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
yes_no_choice = (
    ('yes', _('Да')),
    ('no', _('Нет'))
)
division_choice = (
    ('div1', _('Дивизион 1 – ученики гимназий, лицеев, областных, частных и специализированных школ.')),
    ('div2', _('Дивизион 2 – ученики городских, районных и сельских общеобразовательных школ.'))
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
    'YesNoField': forms.ChoiceField(choices=yes_no_choice),
    'DivisionChoiceField': forms.ChoiceField(choices=division_choice),
}


def get_field(field):
    label = None

    if get_language() == 'en' and 'name_en' in field:
        label = field['name_en']
    elif get_language() == 'kk' and 'name_kk' in field:
        label = field['name_kk']
    elif 'name_ru' in field:
        label = field['name_ru']

    if field.get('field', None) in fields:
        res = copy.copy(fields[field['field']])
        if label is not None:
            res.label = label
    else:
        res = forms.CharField(label=label or field['name'])

    if "not_required" in field:
        res.required = False

    return res
