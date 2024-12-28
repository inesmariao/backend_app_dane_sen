# Generated by Django 5.1.3 on 2024-12-19 23:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_diversa', '0003_response_options_multiple_selected'),
    ]

    operations = [
        migrations.AddField(
            model_name='subquestion',
            name='custom_identifier',
            field=models.CharField(blank=True, help_text='Identificador personalizado para la subpregunta, como 17.1 o 18.2. Opcional, pero único si se usa.', max_length=20, null=True, unique=True),
        ),
    ]
