import json
from app_diversa.models import Chapter, Survey
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_diversa/fixtures/app_diversa_chapter.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            survey = Survey.objects.get(id=item["survey_id"])
            Chapter.objects.update_or_create(
                id=item["id"],
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "survey": survey
                }
            )
            print(f"✔ Capítulo insertado: {item['name']}")
    print("Capítulos cargados")

run()
