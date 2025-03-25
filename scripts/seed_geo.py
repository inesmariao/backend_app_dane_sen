import json
from app_geo.models import Country, Department, Municipality
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def seed_countries():
    with open("app_geo/fixtures/app_geo_country.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            Country.objects.update_or_create(
                id=item["id"],
                defaults={
                    "spanish_name": item["spanish_name"],
                    "english_name": item["english_name"],
                    "numeric_code": item["numeric_code"],
                    "alpha_2": item["alpha_2"],
                    "alpha_3": item["alpha_3"]
                }
            )
            print(f"✔ País insertado: {item['spanish_name']}")
    print("✅ Países cargados\n")


def seed_departments():
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
            print(f"✔ Departamento insertado: {item['name']}")
    print("✅ Departamentos cargados\n")


def seed_municipalities():
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
            print(f"✔ Municipio insertado: {item['name']}")
    print("✅ Municipios cargados\n")


def run():
    seed_countries()
    seed_departments()
    seed_municipalities()

run()
