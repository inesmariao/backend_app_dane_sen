from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, WelcomeView, SurveyViewSet, QuestionViewSet, OptionViewSet, CustomTokenObtainPairView

# Configuración del router
router = DefaultRouter()
router.register('surveys', SurveyViewSet, basename='survey')
router.register('questions', QuestionViewSet, basename='question')
router.register('options', OptionViewSet, basename='option')

# Lista de URLs
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('welcome/', WelcomeView.as_view(), name='welcome'),
    path('token/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('', include(router.urls)),
]
