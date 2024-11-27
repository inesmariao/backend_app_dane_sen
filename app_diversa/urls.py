from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import welcome_view, RegisterView, LoginView, SurveyViewSet, QuestionViewSet, OptionViewSet

# Configuración del router
router = DefaultRouter()
router.register('surveys', SurveyViewSet, basename='survey')
router.register('questions', QuestionViewSet, basename='question')
router.register('options', OptionViewSet, basename='option')

# Lista de URLs
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('welcome/', welcome_view, name='welcome'),
    path('', include(router.urls)),
]
