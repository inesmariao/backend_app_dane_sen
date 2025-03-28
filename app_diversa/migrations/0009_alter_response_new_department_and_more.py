# Generated by Django 5.1.3 on 2025-03-10 22:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_diversa', '0008_question_note_subquestion_note_alter_option_note'),
        ('app_geo', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='response',
            name='new_department',
            field=models.ForeignKey(blank=True, help_text='Nuevo departamento seleccionado (pregunta 8).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='responses_new_departments', to='app_geo.department'),
        ),
        migrations.AlterField(
            model_name='response',
            name='new_municipality',
            field=models.ForeignKey(blank=True, help_text='Nuevo municipio seleccionado (pregunta 8).', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='responses_new_municipalities', to='app_geo.municipality'),
        ),
        migrations.CreateModel(
            name='SurveyAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_lived_in_colombia', models.BooleanField(help_text='Indica si el participante ha vivido en Colombia durante los últimos 5 años.')),
                ('birth_day', models.IntegerField(blank=True, help_text='Día de nacimiento del participante (1-31).', null=True)),
                ('birth_month', models.IntegerField(blank=True, help_text='Mes de nacimiento del participante (1-12).', null=True)),
                ('birth_year', models.IntegerField(blank=True, help_text='Año de nacimiento del participante.', null=True)),
                ('rejection_note', models.CharField(blank=True, help_text='Razón por la cual el usuario fue rechazado si no cumple con los requisitos.', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha y hora en que se registró el intento de la encuesta.')),
                ('survey', models.ForeignKey(help_text='Encuesta que el usuario intentó completar.', on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='app_diversa.survey')),
                ('user', models.ForeignKey(help_text='Usuario que intentó completar la encuesta.', on_delete=django.db.models.deletion.CASCADE, related_name='survey_attempts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='response',
            name='survey_attempt',
            field=models.ForeignKey(blank=True, help_text='Intento de la encuesta asociado a esta respuesta.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='app_diversa.surveyattempt'),
        ),
    ]
