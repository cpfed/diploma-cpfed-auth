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
    actions = ["send_email", "tolower"]

    @admin.action(description=_("Отправить письмо на почту"))
    def send_email(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        selected = queryset.values_list("pk", flat=True)
        return HttpResponseRedirect(reverse("send_emails") + '?ids=' + ','.join(str(x) for x in selected))

    @admin.action(description=_("tolower"))
    def tolower(self, request, queryset):
        us = MainUser.objects.all().values_list("handle", flat=True)
        us = list(x.lower() for x in us)
        if len(set(us)) == len(us):
            render(request, 'admin/result_message.html', {'message': 'OK'})
        wrong = {u:0 for u in us}
        for u in us:
            wrong[u] = wrong[u]+1
        return render(request, 'admin/result_message.html', {'message': list(u for u in wrong if wrong[u] > 1)})

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
