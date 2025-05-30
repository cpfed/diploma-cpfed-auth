"""
URL configuration for cpfed project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from .views import health_check

# Non-localized URLs
urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('telegram/', include('telegram_bot.urls'))
]

# Localized URLs
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('', include('contest.urls')),
    path('', include('locations.urls')),
)

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()