import json
from app_diversa.models import SystemMessage
from django.db import connection

print("Conectado a:", connection.settings_dict["HOST"])

def run():
    with open("app_diversa/fixtures/app_diversa_systemmessage.json", mode='r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            SystemMessage.objects.update_or_create(
                id=item["id"],
                defaults={
                    "key": item["key"],
                    "title": item["title"],
                    "content": item["content"],
                    "is_active": item["is_active"]
                }
            )
            print(f"✔ Mensaje insertado: {item['key']}")
    print("Mensajes del sistema cargados")

run()
