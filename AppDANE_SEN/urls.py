from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="AppDANE_SEN API",
        default_version='v1',
        description="Documentación de la API de AppDANE_SEN",
        terms_of_service="https://www.tusitio.com/terminos/",
        contact=openapi.Contact(email="imoliverosh@dane.gov.co"),
        license=openapi.License(name="Licencia DANE"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Administración de Django
    path('admin/', admin.site.urls),

    # Versionamiento de la API para app_diversa
    path('app_diversa/', include('app_diversa.urls')),

    # Versionamiento de la API para users
    path('users/', include('users.urls')),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
