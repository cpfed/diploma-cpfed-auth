from django.contrib import admin
from django.utils.translation import gettext_lazy as _

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
