from django.urls import path
from .views import contest_reg, main_page, upload_contest_results

urlpatterns = [
    path('contestRegistration/<int:contest_id>/', contest_reg, name='contestRegistration'),
    path('', main_page, name='main_page'),

    path('upload_contest_results/', upload_contest_results, name='upload_contest_results')
]