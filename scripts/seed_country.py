import json
from app_geo.models import Country
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
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
            print(f"✔ Insertado: {item['spanish_name']}")

run()

