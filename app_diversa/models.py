
from django.db import models
from django.conf import settings

class Module(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Survey(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

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
    data_type = models.CharField(max_length=50, blank=True, null=True)  # 'integer', 'string', etc.
    min_value = models.IntegerField(blank=True, null=True)  # Para valores numéricos
    max_value = models.IntegerField(blank=True, null=True)  # Para valores numéricos
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_other = models.BooleanField(default=False)  # Indica si es una opción "Otro".
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.text
    
class Response(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='responses')
    response_text = models.TextField(null=True, blank=True)  # Para texto
    response_number = models.IntegerField(null=True, blank=True)  # Para números
    option_selected = models.ForeignKey('Option', on_delete=models.SET_NULL, null=True, blank=True)  # Para preguntas cerradas
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Respuesta de {self.user} a {self.question.text}"
    
    def clean(self):
        """
        Validaciones personalizadas para asegurar que las respuestas cumplan 
        con los requisitos según el tipo de pregunta.
        """
        from django.core.exceptions import ValidationError

        if self.question.question_type == 'open':  # Pregunta abierta
            if self.response_number is not None and self.response_text is not None:
                raise ValidationError("Solo se puede llenar `response_text` o `response_number`.")
            if self.response_number is None and self.response_text is None:
                raise ValidationError("Debe proporcionar una respuesta abierta (texto o número).")

        elif self.question.question_type == 'closed':  # Pregunta cerrada
            if not self.option_selected:
                raise ValidationError("Debe seleccionar una opción para una pregunta cerrada.")

        super().clean()

