# Generated by Django 5.1.3 on 2024-12-06 02:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_diversa', '0004_chapter_updated_at_option_updated_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_multiple',
            field=models.BooleanField(default=False, help_text='Indica si la pregunta permite seleccionar múltiples opciones.'),
        ),
    ]
