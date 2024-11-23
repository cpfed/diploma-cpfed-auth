from django.contrib import admin
from .models import MainUser, PasswordRecovery

# Register your models here.

admin.site.register(MainUser)
admin.site.register(PasswordRecovery)
