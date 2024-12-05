from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, response
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms.models import fields_for_model
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError

from .models import Contest, UserContest
from .forms import ContestRegistrationForm
from authentication.forms import get_user_form


# Create your views here.


def contest_reg(request: HttpResponse, contest_id: int):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

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
    return render(request, 'crk_reg.html', {
        'form': form,
        'form_name': _('Регистрация на чемпионат'),
    })


def main_page(request: HttpResponse):
    if settings.HOME_PAGE_URL != './':
        return redirect(settings.HOME_PAGE_URL)
    contests = {x: False for x in Contest.objects.all().order_by('-id')}
    if request.user.is_authenticated:
        for contets_reg in UserContest.objects.filter(user=request.user):
            contests[contets_reg.contest] = True
    return render(request, 'main_page.html', {'contests': contests})
