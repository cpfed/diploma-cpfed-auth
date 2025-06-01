import json
import jwt

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, response, JsonResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlencode
from django.utils.crypto import get_random_string
from django.db.utils import IntegrityError
from django.db.models.functions import Concat, RowNumber, Coalesce
from django.db.models import Q, Sum, Value, Window, OuterRef, Exists, Subquery, FloatField, Case, When, F, Func
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_page
from django.utils import timezone

from django_cte import With
from ipware import get_client_ip

from .models import Contest, UserContest, ContestResult
from .forms import ContestRegistrationForm
from .utils import contest_parser, gp100, esep, json_encoder, kcpc_res
from utils.funcs import gen_unambiguous_random_string
from authentication.forms import get_user_form
from authentication.models import OnsiteLogin, OnsiteLoginLogs
from locations.models import Region


def contest_reg(request: HttpResponse, contest_id: int):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(f"{reverse('login')}?{urlencode({'next': request.path})}")

    contest = get_object_or_404(Contest, id=contest_id)

    if not contest.registration_open and not (request.user.is_staff or request.user.is_superuser):
        return render(request, 'result_message.html', {'message': _('Регистрация закрыта')})

    if UserContest.objects.filter(user=request.user, contest=contest).exists():
        return render(request, 'result_message.html', {'message': _('Вы уже зарегистрированы!')})

    form = ContestRegistrationForm(contest, request.user)
    if request.method == 'POST':
        form = ContestRegistrationForm(contest, request.user, None, request.POST)
        # to update user data from registration
        user_form = get_user_form(contest.user_fields)(request.POST, instance=request.user)
        if form.is_valid() and user_form.is_valid():
            contest_data = dict()
            for field, value in form.cleaned_data.items():
                if field not in contest.user_fields:
                    contest_data[field] = value

            user_reg = UserContest(user=request.user, contest=contest, additional_fields=contest_data)
            user_reg.save()

            # update fields only from form
            user_form.save(commit=False)
            request.user.save(update_fields=user_form.cleaned_data.keys())

            esep.reg_users_to_esep_organization(contest, request.user.email)

            return render(request, 'contest_reg_success.html', {'message': contest.text_after_submit})
        # add all errors for user fields
        for field, errs in user_form.errors.items():
            for err in errs:
                if err not in form.errors.get(field, []):
                    form.add_error(field, err)
    return render(request, 'contest_registration.html', {
        'form': form,
        'form_name': contest.name,
        'contest': contest
    })


def contest_reg_guide(request: HttpResponse, contest_id: int):
    return render(request, 'contest_reg_guide.html',
                  {'contest_reg_link': reverse('contestRegistration', args=[contest_id])})


def main_page(request: HttpResponse):
    if 'token' in request.GET and settings.OQYLYK_JWT_SECRET != '':
        token = request.GET['token']
        try:
            payload = jwt.decode(token, settings.OQYLYK_JWT_SECRET, algorithms=['HS256'])
            handle = payload.get('handle', '')
            secret_code = payload.get('secret_code', '')
            ol = OnsiteLogin.objects.get(user__handle=handle, secret_code=secret_code)
            if ol.is_still_valid:
                client_ip, _ = get_client_ip(request)
                # OnsiteLoginLogs(onsite_login=ol, ip_address=client_ip).save()
                login(request, ol.user)
                if ol.contest is not None:
                    return HttpResponseRedirect(f'{reverse("login")}?contest={ol.contest.pk}')
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass
        except (KeyError, UnicodeDecodeError, ValueError, ObjectDoesNotExist):
            pass

    contests = Contest.objects.filter(show_on_main_page=True).order_by('level_on_main_page', '-id')
    if request.user.is_authenticated:
        user_contest_exists = UserContest.objects.filter(user=request.user, contest=OuterRef('pk'))
        contests = contests.annotate(is_registered=Exists(user_contest_exists))
    return render(request, 'main_page.html', {'contests': contests})


def upload_contest_results(request: HttpResponse):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied()

    class HTMLForm(forms.Form):
        link = forms.CharField(max_length=1000, label=_('Ссылка на API с результатами контеста'))
        need_gp = forms.BooleanField(label=_('Добавить очки по GP100?'))

    if request.method == 'POST':
        form = HTMLForm(request.POST)
        list_skipped = []
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
                    user_reg = UserContest.objects.get(user=user, contest=contest)
                except ObjectDoesNotExist:
                    list_skipped.append(res.user)
                    continue
                cr = ContestResult(user_reg=user_reg, rank=rank)
                if form.cleaned_data['need_gp']:
                    cr.points = gp100.estimate_point_gp100(rank, res.score, results[0].score, len(results))
                cr.save()
            return render(request, 'admin/result_message.html', {
                'message': f'Успешно загружены результаты контеста, регистрации нет у {len(list_skipped)} пользователей: {", ".join(list_skipped)}'})
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


# @cache_page(60 * 60)
def api_contest_results(request: HttpResponse):
    data = kcpc_res.get_kcpc_res()

    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 20))
    fullname = request.GET.get("fullname", "")
    region_id = request.GET.get("region_id", None)

    regions = {x["id"]: x for x in Region.objects.all().values("id", "name")}
    print(regions)

    res = (x for x in data)
    if fullname:
        res = (x for x in res if fullname in x["full_name"])
    if region_id:
        res = (x for x in res if fullname in x["region_id"])
    res = [{
        "points": [round(f, 3) for f in x["result_array"]],
        "total_points": round(x["total_points"], 3),
        "fullname": x["full_name"],
        "rank": x["rank"],
        "region": regions[x["region_id"]]
    } for x in list(res)[(page - 1) * limit:page * limit]]
    return render(request, 'admin/result_message.html', {'message': str(
    {
        "count": len(data),
        "next": None,
        "previous": None,
        "results": res
    })})
    # return JsonResponse({
    #     "count": len(data),
    #     "next": None,
    #     "previous": None,
    #     "results": res
    # })


def create_onsite_login(request: HttpResponse):
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        raise PermissionDenied()

    class HTMLForm(forms.Form):
        exp_date = forms.DateTimeField(label=_('Expiration date'), initial=timezone.now())  # "%Y-%m-%d %H:%M:%S"
        secret_code_prefix = forms.CharField(max_length=100, label=_('Secret code prefix'))
        is_one_time = forms.BooleanField(label='Is one time?', required=False)
        create_new = forms.BooleanField(label='Create new code?', required=False)

    if request.method == 'POST':
        form = HTMLForm(request.POST)
        if form.is_valid():
            contest = get_object_or_404(Contest, pk=int(request.GET['id']))
            res = []
            for user in get_user_model().objects.filter(contests__contest=contest):
                if user.is_staff:
                    continue
                try:
                    filt = OnsiteLogin.objects.filter(user=user, contest=contest).order_by("-id")
                    ol = filt[0]
                except IndexError:
                    pass
                else:
                    if not form.cleaned_data["create_new"]:
                        ol.expiration_date = form.cleaned_data["exp_date"]
                        ol.is_one_time = form.cleaned_data["is_one_time"]
                        ol.save()
                        res.append((user.handle, user.email, ol.secret_code))
                        continue
                code = form.data["secret_code_prefix"] + gen_unambiguous_random_string()
                ol = OnsiteLogin(user=user, contest=contest, expiration_date=form.cleaned_data["exp_date"],
                                 secret_code=code, is_one_time=form.cleaned_data["is_one_time"])
                ol.save()
                res.append((user.handle, user.email, code))
            return render(request, 'admin/result_message.html', {
                'message': f'Успешно загружены onsite login, codes: {res}'})
    form = HTMLForm()
    return render(request, 'admin/form.html', {'form': form, 'form_name': 'Fill pls'})
