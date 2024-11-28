from django.urls import path
from .views import RegisterView, LoginView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

# Rutas de la API versión 1 para usuarios
urlpatterns = [
    # Registro de usuarios
    path('register/', RegisterView.as_view(), name='v1-register'),

    # Inicio de sesión
    path('login/', LoginView.as_view(), name='v1-login'),

    # Obtención de tokens JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='v1-token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='v1-token_refresh'),
]