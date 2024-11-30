from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, DepartmentViewSet, MunicipalityViewSet, FileUploadView
from . import views

# Configuración del enrutador para manejar CRUD automáticamente
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='countries')
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'municipalities', MunicipalityViewSet, basename='municipalities')

# Definición de las rutas principales
urlpatterns = [
    # Incluye los endpoints de CRUD generados automáticamente
    path('', include(router.urls)),
    
    path('departments/', views.get_departments, name='get_departments'),
    
    path('municipalities/<int:department_code>/', views.get_municipalities, name='get_municipalities'),

    # Endpoint para cargar archivos JSON o CSV
    path('upload/', FileUploadView.as_view(), name='file-upload'),
]
