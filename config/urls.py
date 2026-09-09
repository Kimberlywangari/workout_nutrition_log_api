"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.http import JsonResponse
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

from workout.views import LogoutView, RegisterView
from django.db import connection

def health_check(request):
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    status = 200 if db_ok else 503
    return JsonResponse({"status": "ok" if db_ok else "unhealthy", "database": db_ok}, status=status)


def home(request):
    return JsonResponse({"status": "API is running"})


urlpatterns = [
    path("health/", health_check),
    path('admin/', admin.site.urls),
    path('api/', include('workout.urls')),
    path('api/', include('nutrition.urls')),
    path('', home),
    path('api/login/', obtain_auth_token, name='api_login'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/register/', RegisterView.as_view(), name='api_register'),
]
