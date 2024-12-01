from django.urls import path
from .views import contest_reg, main_page

urlpatterns = [
    path('contestRegistration/<int:contest_id>/', contest_reg, name='contestRegistration'),
    path('', main_page, name='main_page'),
]