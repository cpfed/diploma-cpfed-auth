import time

from django import forms
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.http import HttpResponse, response
from django.core.exceptions import PermissionDenied
from django.db.models import ObjectDoesNotExist

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


def register_users_from_list(request: HttpResponse):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied()

    class Form(forms.Form):
        userlist = forms.FileField(widget=forms.ClearableFileInput(), label='CSV список пользователей')
        subject = forms.CharField(max_length=100, label=_('Тема письма'))
        file_new = forms.FileField(widget=forms.ClearableFileInput(), label='Для новых пользователей')
        file_was = forms.FileField(widget=forms.ClearableFileInput(), label='Для существующих пользователей')

    if request.method == 'POST':
        form = Form(request.POST, request.FILES)
        if form.is_valid():
            for_new = form.cleaned_data['file_new'].read().decode(encoding='utf-8')
            for_was = form.cleaned_data['file_was'].read().decode(encoding='utf-8')
            handle_ind = 1

            result = []

            userlist = form.cleaned_data['userlist'].read().decode(encoding='utf-8')
            try:
                for row in map(lambda s: s.split(','), userlist.split('\n')):
                    email = row[0]
                    pn = row[1]
                    last_name, first_name, *a = map(lambda s: ' '.join(s.capitalize().split('_')), row[2].split())
                    try:
                        try:
                            MainUser.objects.get(email=email)
                            err = send_emails([email], form.cleaned_data['subject'], None, for_was)
                        except ObjectDoesNotExist:
                            password = get_random_string(10)
                            handle = None
                            while handle is None:
                                h = f'teacher_{handle_ind}'
                                if not MainUser.objects.filter(handle=h).exists():
                                    handle = h
                                handle_ind += 1
                            try:
                                user = MainUser(handle=handle, email=email, first_name=first_name, last_name=last_name, phone_number=pn)
                                user.set_password(password)
                                user.save()
                                err = send_emails([email], form.cleaned_data['subject'], None, for_new.format(login=handle, password=password))
                            except: # phone number error
                                MainUser.objects.get(email=email)
                                err = send_emails([email], form.cleaned_data['subject'], None, for_was)
                    except Exception as e:
                        err = str(e)
                    result.append(f"{email}: {'OK' if err is None else err}")
                    time.sleep(1)
                return render(request, 'admin/result_message.html', {'message': '\n'.join(result)})
            except Exception as e:
                return render(request, 'admin/result_message.html', {'message': str(e)})
    form = Form()
    return render(request, 'admin/form.html', {'form': form, 'form_name': 'Зарегистрировать пользователей'})
