# Generated by Django 5.1.3 on 2024-12-19 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_diversa', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='options_multiple_selected',
            field=models.JSONField(blank=True, help_text='Opciones seleccionadas para preguntas de selección múltiple (almacenadas como JSON).', null=True),
        ),
    ]
