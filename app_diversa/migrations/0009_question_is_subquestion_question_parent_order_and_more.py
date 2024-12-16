# Generated by Django 5.1.3 on 2024-12-11 00:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_diversa', '0008_rename_text_option_text_option_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_subquestion',
            field=models.BooleanField(default=False, help_text='Indica si esta pregunta es una subpregunta.'),
        ),
        migrations.AddField(
            model_name='question',
            name='parent_order',
            field=models.PositiveIntegerField(blank=True, help_text='Número de la pregunta padre a la que pertenece esta subpregunta. Nulo si no aplica.', null=True),
        ),
        migrations.AddField(
            model_name='question',
            name='parent_question',
            field=models.ForeignKey(blank=True, help_text='Pregunta padre para subpreguntas en una matriz.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subquestions', to='app_diversa.question'),
        ),
    ]