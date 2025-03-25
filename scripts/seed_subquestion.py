import json
from app_diversa.models import SubQuestion
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_diversa/fixtures/app_diversa_subquestion.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            SubQuestion.objects.update_or_create(
                id=item["id"],
                defaults={
                    "custom_identifier": item["custom_identifier"],
                    "subquestion_order": item["subquestion_order"],
                    "text_subquestion": item["text_subquestion"],
                    "instruction": item["instruction"],
                    "subquestion_type": item["subquestion_type"],
                    "min_value": item["min_value"],
                    "max_value": item["max_value"],
                    "is_multiple": item["is_multiple"],
                    "is_required": item["is_required"],
                    "parent_question_id": item["parent_question_id"],
                    "note": item["note"],
                    "is_other": item["is_other"]
                }
            )
            print(f"✔ Subpregunta insertada: {item['text_subquestion']}")
    print("Subpreguntas cargadas")

run()
