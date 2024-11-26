from django.db import models

class Module(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Survey(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    QUESTION_TYPES = [
        ('open', 'Pregunta Abierta'),
        ('closed', 'Pregunta Cerrada'),
        ('likert', 'Escala Likert'),
        ('rating', 'Escala de Puntuación'),
        ('matrix', 'Pregunta Matricial'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_other = models.BooleanField(default=False)  # Indica si es una opción "Otro".
    created_at = models.DateTimeField(auto_now_add=True)

