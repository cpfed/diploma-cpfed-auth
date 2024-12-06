from django.urls import path
from authentication.views import user_management, password_recovery

urlpatterns = [
    path('login/', user_management.user_login, name='login'),
    path('register/', user_management.user_new, name='register'),
    path('register/<uuid:token>', user_management.user_activate),
    path('logout/', user_management.user_logout, name='logout'),
    path('profile/', user_management.user_profile, name='profile'),

    path('passwordRecovery/', password_recovery.password_recovery_request, name='pass_rec'),
    path('passwordRecovery/<uuid:token>', password_recovery.password_recovery),
]