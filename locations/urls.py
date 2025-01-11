from django.urls import path
from .views import api_regions

urlpatterns = [
    path('api/regions/', api_regions),
]