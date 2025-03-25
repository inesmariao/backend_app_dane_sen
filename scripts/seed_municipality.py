import json
from app_geo.models import Municipality, Department
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_geo/fixtures/app_geo_municipality.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            department = Department.objects.get(code=item["department_code"])
            Municipality.objects.update_or_create(
                id=item["id"],
                defaults={
                    "code": item["code"],
                    "name": item["name"],
                    "department_code": department.code
                }
            )
            print(f"  ✔ Municipio insertado: {item['name']}")
    print("✔ Municipios cargados")

run()
