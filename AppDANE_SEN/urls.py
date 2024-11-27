from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app_diversa.urls')),
    path('users/', include('users.urls')),
    
]
