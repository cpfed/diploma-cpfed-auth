from django.urls import path
from .views import contest_reg, main_page

urlpatterns = [
    path('contestRegistration/<int:constest_id>/', contest_reg),
    path('', main_page),
]