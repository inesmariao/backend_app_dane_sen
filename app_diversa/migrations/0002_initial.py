# Generated by Django 5.1.3 on 2024-11-27 21:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_diversa', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='app_diversa.survey'),
        ),
    ]
