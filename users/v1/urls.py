from django.urls import path, include
from .views import RegisterView, LoginView, CustomTokenObtainPairView, UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

# Configuración del router para vistas basadas en modelos
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

# Rutas específicas de la API v1
urlpatterns = [
    # CRUD de usuarios a través del router
    path('', include(router.urls)),

    # Registro de usuarios
    path('register/', RegisterView.as_view(), name='v1-register'),

    # Inicio de sesión
    path('login/', LoginView.as_view(), name='v1-login'),

    # Rutas para manejo de tokens JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='v1-token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='v1-token_refresh'),
]
