import json
from app_geo.models import Department
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_geo/fixtures/app_geo_department.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            Department.objects.update_or_create(
                id=item["id"],
                defaults={
                    "code": item["code"],
                    "name": item["name"],
                    "country_numeric_code": item["country_numeric_code"]
                }
            )
            print(f"  ✔ Departamento insertado: {item['name']}")
    print("✅ Departamentos cargados")

run()