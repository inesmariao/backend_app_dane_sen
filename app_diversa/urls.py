from django.urls import path, include

urlpatterns = [
    # Rutas para la versión 1 de la API
    path('v1/', include('app_diversa.v1.urls')),
]
