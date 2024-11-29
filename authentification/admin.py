from django.contrib import admin
from .models import MainUser, PasswordRecovery, UserActivation

# Register your models here.

admin.site.register(MainUser)
admin.site.register(PasswordRecovery)
admin.site.register(UserActivation)

