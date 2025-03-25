import json
from app_diversa.models import Survey
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_diversa/fixtures/app_diversa_survey.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            Survey.objects.update_or_create(
                id=item["id"],
                defaults={
                    "name": item["name"],
                    "description_name": item["description_name"],
                    "title": item["title"],
                    "description_title": item["description_title"]
                }
            )
            print(f"✔ Encuesta insertada: {item['title']}")
    print("Encuestas cargadas")

run()
