from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import WelcomeView, SurveyViewSet, QuestionViewSet, OptionViewSet, SubmitResponseView

# Configuración del router
router = DefaultRouter()
router.register('surveys', SurveyViewSet, basename='survey')
router.register('questions', QuestionViewSet, basename='question')
router.register('options', OptionViewSet, basename='option')

# Lista de URLs
urlpatterns = [
    path('welcome/', WelcomeView.as_view(), name='welcome'),
    path('submit-response/', SubmitResponseView.as_view(), name='submit-response'),
    path('', include(router.urls)),
]
