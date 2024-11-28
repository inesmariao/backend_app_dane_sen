from django.urls import path, include

# Enrutador principal de las versiones de la API para usuarios
urlpatterns = [
    # Version 1 de la API
    path('v1/', include('users.v1.urls')),

]
