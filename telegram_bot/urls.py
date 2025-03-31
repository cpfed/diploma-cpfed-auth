from django.urls import path
from . import views

urlpatterns = [
    path('webhook/<str:token>', views.telegram_webhook, name='telegram_webhook'),
    path('login/', views.telegram_login, name='telegram_login'),
    path('broadcast/', views.telegram_broadcast, name='telegram_broadcast'),
]