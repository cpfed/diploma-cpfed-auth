from django import forms
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, response
from django.core.exceptions import PermissionDenied

from authentication.models import MainUser
from .services.send_email import send_emails


def custom_emails_view(request: HttpResponse):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied()

    class HTMLForm(forms.Form):
        subject = forms.CharField(max_length=100, label=_('Тема письма'))
        file = forms.FileField(widget=forms.ClearableFileInput())

    if request.method == 'POST':
        form = HTMLForm(request.POST, request.FILES)
        if form.is_valid() and form.cleaned_data['file'].name.endswith('.html'):
            file = form.cleaned_data['file'].read()
            user_ids = map(int, request.GET['ids'].split(','))
            emails = MainUser.objects.filter(pk__in=user_ids).values_list('email', flat=True)
            err = send_emails(emails, form.cleaned_data['subject'], str(file, encoding='utf-8'))
            return render(request, 'admin/result_message.html',
                          {'message': _('Письма успешно отправлены' if err is None else 'Ошибка: ' + str(err))})
    form = HTMLForm()
    return render(request, 'admin/form.html', {'form': form, 'form_name': _('Выберите шаблон HTML для отправки')})
