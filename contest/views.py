from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, response, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlencode
from django.utils.crypto import get_random_string
from django.db.utils import IntegrityError
from django.db.models.functions import Concat, RowNumber
from django.db.models import Q, Sum, Value, Window
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ObjectDoesNotExist

from django_cte import With

from .models import Contest, UserContest, ContestResult
from .forms import ContestRegistrationForm
from .utils import contest_parser, gp100
from authentication.forms import get_user_form
from locations.models import Region


def contest_reg(request: HttpResponse, contest_id: int):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f"{reverse('login')}?{urlencode({'next': request.path})}")

    contest = get_object_or_404(Contest, id=contest_id)

    if not contest.registration_open and not (request.user.is_staff or request.user.is_superuser):
        return render(request, 'result_message.html', {'message': _('Регистрация закрыта')})

    user_reg = UserContest.objects.filter(user=request.user, contest=contest)
    user_reg = (user_reg[0] if len(user_reg) else None)
    if user_reg is not None:
        return render(request, 'result_message.html', {'message': _('Вы уже зарегистрированы!')})

    form = ContestRegistrationForm(contest, request.user, user_reg)
    if request.method == 'POST':
        form = ContestRegistrationForm(contest, request.user, user_reg, request.POST)
        # to update user data from registration
        user_form = get_user_form(contest.user_fields)(request.POST, instance=request.user)
        if form.is_valid() and user_form.is_valid():
            contest_data = dict()
            for field, value in form.cleaned_data.items():
                if field not in contest.user_fields:
                    contest_data[field] = value

            user_reg, created = UserContest.objects.get_or_create(user=request.user, contest=contest)
            user_reg.additional_fields = contest_data
            user_reg.save()

            user_form.save()

            res = _('Вы успешно зарегистрированы!')
            if contest.text_after_submit:
                res += "<br/>" + contest.text_after_submit

            return render(request, 'result_message.html', {'message': res})
        # add all errors for user fields
        for field, errs in user_form.errors.items():
            for err in errs:
                if err not in form.errors.get(field, []):
                    form.add_error(field, err)
    was_reg = UserContest.objects.filter(user=request.user, contest=contest).exists()

    return render(request, 'contest_registration.html', {
        'form': form,
        'form_name': (contest.name if not was_reg else _('Изменить регистрацию')),
        'contest': contest
    })


def main_page(request: HttpResponse):
    contests = {x: False for x in Contest.objects.filter(show_on_main_page=True).order_by('level_on_main_page', '-id')}
    if request.user.is_authenticated:
        for contests_reg in UserContest.objects.filter(user=request.user, contest__show_on_main_page=True):
            contests[contests_reg.contest] = True
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


def register_on_contest(request: HttpResponse):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied()

    class Form(forms.Form):
        userlist = forms.FileField(widget=forms.ClearableFileInput(), label='Cписок пользователей')
        need_reg = forms.BooleanField(label='Регистрировать на контест?', required=False)
        need_ch_pass = forms.BooleanField(label='Изменить пароль?', required=False)
        show_info = forms.BooleanField(label='Показать информацию о пользователе', required=False)
        by_handle = forms.BooleanField(label='Искать по хэндлу?', required=False)

    if request.method == 'POST':
        form = Form(request.POST, request.FILES)
        if form.is_valid():
            result = []
            userlist = form.cleaned_data['userlist'].read().decode(encoding='utf-8')

            contest = Contest.objects.get(id=int(request.GET['id']))

            for email in userlist.split(','):
                try:
                    user = get_user_model().objects.get(
                        **{('handle' if form.cleaned_data['by_handle'] else 'email'): email})
                except ObjectDoesNotExist:
                    result.append(f"{email}: not exist")
                else:
                    if form.cleaned_data['need_reg']:
                        UserContest.objects.get_or_create(user=user, contest=contest)
                    if form.cleaned_data['need_ch_pass']:
                        password = get_random_string(10)
                        user.set_password(password)
                        user.save()
                        result.append(f"{email}: {password}")
                    if form.cleaned_data['show_info']:
                        result.append(f"{user.handle},{user.email}")
            return render(request, 'admin/result_message.html', {'message': ';'.join(result)})
    form = Form()
    return render(request, 'admin/form.html', {'form': form, 'form_name': 'Зарегистрировать пользователей'})


def api_contest_results(request: HttpResponse):
    cte = With(
        get_user_model().objects.select_related("region")
        .filter(contests__contest=1)
        .filter(contests__result__isnull=False)
        .annotate(
            points=ArrayAgg("contests__result__points"),
            total_points=Sum("contests__result__points"),
            fullname=Concat("first_name", Value(" "), "last_name"),
            rank=Window(expression=RowNumber(), order_by="-total_points")
        )
        .values("fullname", "points", "total_points", "rank", "region_id")
    )
    data = cte.join(Region, id=cte.col.region_id).with_cte(cte).annotate(
        points=cte.col.points,
        total_points=cte.col.total_points,
        fullname=cte.col.fullname,
        rank=cte.col.rank,
    ).order_by("rank")

    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 20))
    fullname = request.GET.get("fullname", "")
    region_id = request.GET.get("region_id", None)
    if fullname:
        data = data.filter(Q(fullname__icontains=fullname))
    if region_id:
        data = data.filter(Q(id=int(region_id)))
    res = [{
        "points": [round(f, 3) for f in x.points],
        "total_points": round(x.total_points, 3),
        "fullname": x.fullname,
        "rank": x.rank,
        "region": {
            "id": x.id,
            "name": x.name
        }
    } for x in data[(page - 1) * limit:page * limit]]

    return JsonResponse({
        "count": len(data),
        "next": None,
        "previous": None,
        "results": res
    })
