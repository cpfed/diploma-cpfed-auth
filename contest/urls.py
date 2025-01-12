from django.urls import path
from .views import contest_reg, main_page, upload_contest_results, api_contest_results, register_on_contest

urlpatterns = [
    path('contestRegistration/<int:contest_id>/', contest_reg, name='contestRegistration'),
    path('', main_page, name='main_page'),

    path('upload_contest_results/', upload_contest_results, name='upload_contest_results'),
    path('register_on_contest/', register_on_contest, name='register_on_contest'),

    path('api/championship-results/', api_contest_results),
]