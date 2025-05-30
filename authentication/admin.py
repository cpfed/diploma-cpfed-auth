from django.contrib import admin
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import MainUser, PasswordRecovery, UserActivation, OnsiteLogin, OnsiteLoginLogs
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
        q = queryset.exclude(contests__contest__id=self.value())
        return q


class OnlyRegisteredFilter(admin.SimpleListFilter):
    title = _("Только зарегистрированные")
    parameter_name = "onlyreg"

    def lookups(self, request, model_admin):
        contests = Contest.objects.all()
        return [(str(c.id), c.name) for c in contests]

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset
        q = queryset.filter(contests__contest__id=self.value())
        return q


@admin.register(MainUser)
class MainUserAdmin(admin.ModelAdmin):
    list_filter = [OnlyRegisteredFilter, ExcludeRegisteredFilter]
    actions = ["send_email", "register_users"]
    search_fields = ["handle", "first_name", "last_name", "phone_number", "email"]
    exclude = ["groups", "user_permissions"]

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


admin.site.register(OnsiteLoginLogs)


@admin.register(OnsiteLogin)
class OnsiteLoginAdmin(admin.ModelAdmin):
    search_fields = ["user__handle"]
