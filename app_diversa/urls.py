from rest_framework.routers import DefaultRouter
from .views import SurveyViewSet, QuestionViewSet, OptionViewSet

router = DefaultRouter()
router.register('surveys', SurveyViewSet)
router.register('questions', QuestionViewSet)
router.register('options', OptionViewSet)

urlpatterns = router.urls
