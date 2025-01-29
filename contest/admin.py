from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.shortcuts import render

from .models import Contest, UserContest, ContestResult
from .utils import contest_parser, xlsx_response

# Register your models here.

admin.site.register(ContestResult)


@admin.register(UserContest)
class UserContestAdmin(admin.ModelAdmin):
    list_filter = ["contest__name"]


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    actions = ['get_registrations', 'upload_contest_results', 'register_on_contest', 'add_bulk_reg', 'contest_results']

    @admin.action(description="Экспортировать данные зарегистрированных пользователей")
    def get_registrations(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        result = []
        for contest in queryset:
            curres = []
            data = None
            for uc in UserContest.objects.filter(contest=contest):
                uc_reg = uc.get_full_reg
                if data is None:
                    data = {x: str(y) for x, y in data.values()}
                else:
                    data = {x: str(uc_reg[x]) for x in data}
                curres.append(tuple(data.values()))
            curres = [contest.name, tuple(data.keys())] + curres
            result.append(curres)
        return xlsx_response(result)

    @admin.action(description="Экспортировать результаты контеста")
    def contest_results(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        result = []
        for contest in queryset:

            link = 'api/v2/contest'.join(contest.link.split('contest'))
            try:
                results = contest_parser.fetch_contest_results(link)
            except Exception as err:
                return render(request, 'admin/result_message.html', {'message': 'Ошибка: ' + str(err)})
            user_ranks = {r.user: r.rank for r in results}

            user_regs = UserContest.objects.filter(contest=contest).select_related('user', 'contest').all()
            user_regs = sorted(user_regs, key=lambda ur: user_ranks.get(ur.user.handle, len(user_regs)+1))

            curres = []
            data = None
            for uc in user_regs:
                uc_reg = uc.get_full_reg_with_additional_data
                if data is None:
                    data = {x: str(y) for x, y in uc_reg.items()}
                else:
                    data = {x: str(uc_reg[x]) for x in data}
                handle = uc_reg['handle']
                curres.append([str(user_ranks[handle]) if handle in user_ranks else "Не участвовал"] + list(data.values()))

            curres = [contest.name, ['place'] + list(data.keys())] + curres
            result.append(curres)
        return xlsx_response.xlsx_response(result)

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

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
