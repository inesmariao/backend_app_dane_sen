# Generated by Django 5.1.3 on 2025-03-24 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_diversa', '0016_systemmessage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='response',
            name='new_department',
        ),
        migrations.RemoveField(
            model_name='response',
            name='new_municipality',
        ),
    ]
