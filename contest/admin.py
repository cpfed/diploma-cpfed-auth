from django.db import models
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.shortcuts import render
from django.conf import settings

from .models import Contest, UserContest, ContestResult
from .utils import contest_parser, xlsx_response, esep
from .forms import AdminTextAreaWidget


# Register your models here.


class OnlyRegisteredFilter(admin.SimpleListFilter):
    title = "Только зарегистрированные"
    parameter_name = "onlyreg"

    def lookups(self, request, model_admin):
        contests = Contest.objects.all()
        return [(str(c.id), c.name) for c in contests]

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        q = queryset.filter(contest__id=self.value())
        return q


@admin.register(UserContest)
class UserContestAdmin(admin.ModelAdmin):
    list_filter = [OnlyRegisteredFilter]
    search_fields = ["user__handle"]


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    actions = ['contest_results', 'upload_contest_results', 'register_on_contest', 'add_bulk_reg',
               'sync_user_reg_with_esep', 'create_onsite_login']
    formfield_overrides = {
        models.TextField: {'widget': AdminTextAreaWidget},
    }

    @admin.action(description="Экспортировать результаты контеста")
    def contest_results(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        try:
            result = []
            for contest in queryset:
                user_regs = UserContest.objects.filter(contest=contest).select_related('user', 'contest').all()

                sort_by_place = (contest.link is not None)
                if sort_by_place:
                    link = '/api/v2/contest/'.join(contest.link.split('/contest/'))
                    results = contest_parser.fetch_contest_results(link)
                    user_ranks = {r.user: r.rank for r in results}
                    user_regs = sorted(user_regs, key=lambda ur: user_ranks.get(ur.user.handle, len(user_regs) + 1))

                curres = []
                data = {f: None for f in contest.fields_name_list}
                data["email"] = None
                data["handle"] = None

                for uc in user_regs:
                    uc_reg = uc.get_full_reg_with_additional_data
                    data = {x: str(uc_reg.get(x, '')) for x in data}
                    cur_list = list(data.values())
                    if sort_by_place:
                        handle = uc_reg['handle']
                        cur_list.insert(0, str(user_ranks[handle]) if handle in user_ranks else "Не участвовал")
                    curres.append(cur_list)

                curres = [contest.name, (['place'] if sort_by_place else []) + list(data.keys())] + curres
                result.append(curres)
            return xlsx_response.xlsx_response(result)
        except Exception as err:
            # return render(request, 'admin/result_message.html', {'message': f"Ошибка: {err}"})
            raise err

    @admin.action(description="Загрузить результаты контеста")
    def upload_contest_results(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        selected = queryset.values_list("pk", flat=True)
        if len(selected) != 1:
            return render(request, 'admin/result_message.html', {'message': "Должен быть выбран только один контест"})
        return HttpResponseRedirect(reverse("upload_contest_results") + '?id=' + str(selected[0]))

    @admin.action(description="Зарегистрировать пользователей на контест")
    def register_on_contest(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        selected = queryset.values_list("pk", flat=True)
        if len(selected) != 1:
            return render(request, 'admin/result_message.html', {'message': "Должен быть выбран только один контест"})
        return HttpResponseRedirect(reverse("register_on_contest") + '?id=' + str(selected[0]))

    @admin.action(description="Добавить регистрации со старого контеста на новый")
    def add_bulk_reg(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        selected = queryset.values_list("pk", flat=True)
        if len(selected) != 2:
            return render(request, 'admin/result_message.html', {'message': "Должены быть выбраны ровно два контеста"})
        fr, to = sorted(selected)
        contest = Contest.objects.get(id=to)
        for uc in UserContest.objects.filter(contest__id=fr):
            UserContest.objects.get_or_create(user=uc.user, contest=contest,
                                              defaults={"additional_fields": uc.additional_fields})
        return render(request, 'admin/result_message.html', {'message': "ok"})

    @admin.action(description="Синхронизировать регистрaции с есепом")
    def sync_user_reg_with_esep(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        for contest in queryset:
            err = esep.reg_users_to_esep_organization(contest)
            if err is not None:
                return render(request, 'admin/result_message.html',
                              {'message': f"contest: {contest}, error: {str(err)}"})
        return render(request, 'admin/result_message.html', {'message': "ok"})

    @admin.action(description="Сделать onsite login")
    def create_onsite_login(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        selected = queryset.values_list("pk", flat=True)
        if len(selected) != 1:
            return render(request, 'admin/result_message.html', {'message': "Должен быть выбран только один контест"})
        return HttpResponseRedirect(reverse("create_onsite_login") + '?id=' + str(selected[0]))

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions


class ContestResultByContestFilter(admin.SimpleListFilter):
    title = "By contest"
    parameter_name = "contest_filter"

    def lookups(self, request, model_admin):
        contests = Contest.objects.all()
        return [(str(c.id), c.name) for c in contests]

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        q = queryset.filter(user_reg__contest__id=self.value())
        return q


@admin.register(ContestResult)
class ContestResultAdmin(admin.ModelAdmin):
    list_filter = [ContestResultByContestFilter]
    search_fields = ["user_reg__user__handle"]
