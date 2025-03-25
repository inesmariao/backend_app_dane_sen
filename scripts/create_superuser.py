import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AppDANE_SEN.settings")
django.setup()

from users.models import CustomUser

if not CustomUser.objects.filter(username="admin").exists():
    CustomUser.objects.create_superuser(
        username="admin",
        email="imoliverosh@dane.gov.co",
        password="admin123"
    )
    print("Superusuario creado")
else:
    print("Ya existe un superusuario con ese nombre")
