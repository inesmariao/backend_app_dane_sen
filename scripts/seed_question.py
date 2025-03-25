import json
from app_diversa.models import Question
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_diversa/fixtures/app_diversa_question.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            Question.objects.update_or_create(
                id=item["id"],
                defaults={
                    "order_question": item["order_question"],
                    "text_question": item["text_question"],
                    "instruction": item["instruction"],
                    "is_geographic": item["is_geographic"],
                    "geography_type": item["geography_type"],
                    "question_type": item["question_type"],
                    "matrix_layout_type": item["matrix_layout_type"],
                    "data_type": item["data_type"],
                    "min_value": item["min_value"],
                    "max_value": item["max_value"],
                    "is_multiple": item["is_multiple"],
                    "is_required": item["is_required"],
                    "chapter_id": item["chapter_id"],
                    "survey_id": item["survey_id"],
                    "note": item["note"]
                }
            )
            print(f"✔ Pregunta insertada: {item['text_question']}")
    print("Preguntas cargadas")

run()
