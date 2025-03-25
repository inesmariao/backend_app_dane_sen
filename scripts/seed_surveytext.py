import json
from app_diversa.models import SurveyText
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_diversa/fixtures/app_diversa_surveytext.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            SurveyText.objects.update_or_create(
                id=item["id"],
                defaults={
                    "title": item["title"],
                    "description": item["description"],
                    "is_active": item["is_active"],
                    "survey_id": item["survey_id"]
                }
            )
            print(f"✔ Texto insertado: {item['title']}")
    print("Textos de encuesta cargados")

run()
