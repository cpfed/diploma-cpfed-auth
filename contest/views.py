from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, response
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlencode
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django import forms

from .models import Contest, UserContest, ContestResult
from .forms import ContestRegistrationForm
from .utils import contest_parser, gp100
from authentication.forms import get_user_form


def contest_reg(request: HttpResponse, contest_id: int):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f"{reverse('login')}?{urlencode({'next': request.path})}")

    contest = get_object_or_404(Contest, id=contest_id)

    form = ContestRegistrationForm(contest, request.user)
    if request.method == 'POST':
        form = ContestRegistrationForm(contest, request.user, request.POST)
        # to update user data from registration
        user_form = get_user_form(contest.required_fields)(request.POST, instance=request.user)
        if form.is_valid() and user_form.is_valid():
            mem_fields = {x.name for x in get_user_model()._meta.get_fields()}
            contest_data = dict()
            for field, value in form.cleaned_data.items():
                if field not in mem_fields:
                    contest_data[field] = value

            user_reg, created = UserContest.objects.get_or_create(user=request.user, contest=contest)
            user_reg.additional_fields = contest_data
            user_reg.save()

            user_form.save()
            return render(request, 'result_message.html', {'message': _('Вы успешно зарегистрированы!')})
        # add all errors for user fields
        for field, errs in user_form.errors.items():
            for err in errs:
                if err not in form.errors.get(field, []):
                    form.add_error(field, err)
    was_reg = UserContest.objects.filter(user=request.user, contest=contest).exists()
    return render(request, 'crk_reg.html', {
        'form': form,
        'form_name': (_('Регистрация на чемпионат') if not was_reg else _('Изменить регистрацию')),
    })


def main_page(request: HttpResponse):
    contests = {x: False for x in Contest.objects.all().order_by('-id')}
    if request.user.is_authenticated:
        for contets_reg in UserContest.objects.filter(user=request.user):
            contests[contets_reg.contest] = True
    return render(request, 'main_page.html', {'contests': contests})


def upload_contest_results(request: HttpResponse):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied()

    class HTMLForm(forms.Form):
        link = forms.CharField(max_length=1000, label=_('Ссылка на API с результатами контеста'))
        need_gp = forms.BooleanField(label=_('Добавить очки по GP100?'))

    if request.method == 'POST':
        form = HTMLForm(request.POST)
        cnt_skipped = 0
        if form.is_valid():
            contest = get_object_or_404(Contest, pk=int(request.GET['id']))
            ContestResult.objects.filter(user_reg__contest__pk=contest.pk).delete()

            try:
                results = contest_parser.fetch_contest_results(form.cleaned_data['link'])
            except Exception as err:
                return render(request, 'admin/result_message.html', {'message': 'Ошибка: ' + str(err)})

            for rank, res in enumerate(results, start=1):
                try:
                    user = get_user_model().objects.get(handle=res.user)
                except ObjectDoesNotExist:
                    cnt_skipped += 1
                    continue
                    # return render(request, 'admin/result_message.html',
                    #               {'message': f'Не найден пользователь с хэндлом: {res.user}'})
                try:
                    user_reg = UserContest.objects.get(user=user, contest=contest)
                except ObjectDoesNotExist:
                    cnt_skipped += 1
                    continue
                cr = ContestResult(user_reg=user_reg, rank=rank)
                if form.cleaned_data['need_gp']:
                    cr.points = gp100.estimate_point_gp100(rank, res.score, results[0].score, len(results))
                cr.save()
            return render(request, 'admin/result_message.html', {
                'message': f'Успешно загружены результаты контеста, регистрации нет у {cnt_skipped} пользователей: '})
    form = HTMLForm()
    return render(request, 'admin/form.html', {'form': form, 'form_name': _('Загрузить результаты контеста')})


def api_contest_results(request: HttpResponse):
    pass