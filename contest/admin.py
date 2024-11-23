from django.contrib import admin
from .models import Contest, UserContest

# Register your models here.

admin.site.register(Contest)
admin.site.register(UserContest)
