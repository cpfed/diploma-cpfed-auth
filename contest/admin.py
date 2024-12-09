from tempfile import NamedTemporaryFile

from openpyxl import Workbook

from django.contrib import admin
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied

from .models import Contest, UserContest

# Register your models here.

admin.site.register(UserContest)


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    actions = ['get_registrations']

    @admin.action(description="Экспортировать данные зарегистрированных пользователей")
    def get_registrations(self, request, queryset):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied()
        wb = Workbook()
        for contest in queryset:
            wc = wb.create_sheet(title=contest.name)
            wc.append(contest.required_fields)
            for uc in UserContest.objects.filter(contest=contest):
                data = uc.get_full_reg
                wc.append(tuple(str(data[f]) for f in uc.contest.required_fields))
        wb.remove(wb[wb.sheetnames[0]]) # remove default empty sheet
        with NamedTemporaryFile() as tmp:
            wb.save(tmp)
            tmp.seek(0)
            stream = tmp.read()
            return HttpResponse(stream, headers={
                "Content-Type": "application/vnd.ms-excel",
                "Content-Disposition": 'attachment; filename="foo.xlsx"',
            })
    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions