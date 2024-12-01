from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, response
from django.conf import settings
from django.contrib.auth import get_user_model
from django.forms.models import fields_for_model
from django.utils.translation import gettext_lazy as _

from .models import Contest, UserContest
from .forms import ContestRegistrationForm


# Create your views here.


def contest_reg(request: HttpResponse, contest_id: int):
    if not request.user.is_authenticated:
        return redirect(settings.LOGIN_URL)

    error = None
    contest = get_object_or_404(Contest, id=contest_id)
    form = ContestRegistrationForm(contest, request.user)
    if request.method == 'POST':
        form = ContestRegistrationForm(contest, request.user, request.POST)
        if form.is_valid():
            # divide submitted data into remembered fields and contest-specific
            mem_fields = {x.name for x in get_user_model()._meta.get_fields()}
            contest_data = dict()
            for field, value in form.cleaned_data.items():
                if field in mem_fields:
                    setattr(request.user, field, value)
                else:
                    contest_data[field] = value
            request.user.save()
            user_reg = UserContest(user=request.user, contest=contest, additional_fields=contest_data)
            user_reg.save()
            return redirect(settings.AFTER_LOGIN_URL)
        error = str(form.errors)
    return render(request, 'base_form.html', {
        'form': form,
        'error': error,
        'form_name': _('Регистрация на ') + contest.name,
    })


def main_page(request: HttpResponse):
    contests = {x: False for x in Contest.objects.all().order_by('-id')}
    if request.user.is_authenticated:
        for contets_reg in UserContest.objects.filter(user=request.user):
            contests[contets_reg.contest] = True
    return render(request, 'main_page.html', {'contests': contests})
