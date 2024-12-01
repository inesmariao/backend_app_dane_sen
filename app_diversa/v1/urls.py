from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WelcomeView, SurveyViewSet, QuestionViewSet, OptionViewSet, SubmitResponseView, ChapterViewSet, SurveyTextViewSet, ResponseViewSet, SaveGeographicResponseView

# Configuración del router
router = DefaultRouter()
router.register('surveys', SurveyViewSet, basename='survey')
router.register('chapters', ChapterViewSet, basename='chapter')
router.register('questions', QuestionViewSet, basename='question')
router.register('options', OptionViewSet, basename='option')
router.register('survey-texts', SurveyTextViewSet, basename='survey-text')

# Rutas específicas de la API v1
urlpatterns = [
    # Rutas individuales (APIView o Function-based Views)
    path('welcome/', WelcomeView.as_view(), name='v1-welcome'),
    path('submit-response/', SubmitResponseView.as_view(), name='v1-submit-response'),
    path('api/save-geographic-response/', SaveGeographicResponseView.as_view(), name='save_geographic_response'),

    # Rutas de exportación de respuestas
    path('responses/export/<str:format>/', ResponseViewSet.as_view({'get': 'export'}), name='export-responses'),

    # Rutas generadas automáticamente por el router
    path('', include(router.urls)),
]
