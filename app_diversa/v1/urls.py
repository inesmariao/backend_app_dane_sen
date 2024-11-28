from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WelcomeView, SurveyViewSet, QuestionViewSet, OptionViewSet, SubmitResponseView

# Configuración del router
router = DefaultRouter()
router.register('surveys', SurveyViewSet, basename='survey')
router.register('questions', QuestionViewSet, basename='question')
router.register('options', OptionViewSet, basename='option')

# Rutas específicas de la API v1
urlpatterns = [
    # Rutas individuales (APIView o Function-based Views)
    path('welcome/', WelcomeView.as_view(), name='v1-welcome'),
    path('submit-response/', SubmitResponseView.as_view(), name='v1-submit-response'),

    # Rutas generadas automáticamente por el router
    path('', include(router.urls)),
]
