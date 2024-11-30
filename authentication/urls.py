from django.urls import path
from authentication.views import user_management, password_recovery

urlpatterns = [
    path('login/', user_management.user_login),
    path('register/', user_management.user_new),
    path('register/<uuid:token>', user_management.user_activate),
    path('logout/', user_management.user_logout),

    path('passwordRecovery/', password_recovery.password_recovery_request),
    path('passwordRecovery/<uuid:token>', password_recovery.password_recovery),
]