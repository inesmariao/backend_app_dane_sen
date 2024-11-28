from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Administración de Django
    path('admin/', admin.site.urls),

    # Versionamiento de la API para app_diversa
    path('app_diversa/', include('app_diversa.urls')),

    # Versionamiento de la API para users
    path('users/', include('users.urls')),

]
