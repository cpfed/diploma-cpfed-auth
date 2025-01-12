from django.contrib import admin
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import MainUser, PasswordRecovery, UserActivation
from contest.models import Contest, UserContest

# Register your models here.

admin.site.register(PasswordRecovery)
admin.site.register(UserActivation)


class ExcludeRegisteredFilter(admin.SimpleListFilter):
    title = _("Убрать зарегистрированных")
    parameter_name = "excludereg"

    def lookups(self, request, model_admin):
        contests = Contest.objects.all()
        return [(str(c.id), c.name) for c in contests]

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        contest = Contest.objects.get(id=self.value())
        registered_users = UserContest.objects.filter(contest=contest)
        q = queryset.exclude(id__in=registered_users.values_list("user__id", flat=True))
        return q


@admin.register(MainUser)
class MainUserAdmin(admin.ModelAdmin):
    list_filter = ["contests__contest__name", ExcludeRegisteredFilter]
    actions = ["send_email", "register_users"]
    search_fields = ["handle", "first_name", "last_name"]

    @admin.action(description=_("Отправить письмо на почту"))
    def send_email(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        selected = queryset.values_list("pk", flat=True)
        return HttpResponseRedirect(reverse("send_emails") + '?ids=' + ','.join(str(x) for x in selected))

    @admin.action(description=_("Зарегистрировать новых пользователей"))
    def register_users(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        return HttpResponseRedirect(reverse("register_users_from_list"))

    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if "delete_selected" in actions:
    #         del actions["delete_selected"]
    #     return actions
