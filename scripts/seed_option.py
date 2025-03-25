import json
from app_diversa.models import Option
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_diversa/fixtures/app_diversa_option.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            Option.objects.update_or_create(
                id=item["id"],
                defaults={
                    "option_type": item["option_type"],
                    "text_option": item["text_option"],
                    "is_other": item["is_other"],
                    "note": item["note"],
                    "order_option": item["order_option"],
                    "question_id": item["question_id"],
                    "subquestion_id": item["subquestion_id"]
                }
            )
            print(f"✔ Opción insertada: {item['text_option']}")
    print("Opciones cargadas")

run()
