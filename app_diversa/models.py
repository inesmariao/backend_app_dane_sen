from django.db import models
from django.conf import settings

class Module(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="Nombre del módulo. Máximo 100 caracteres."
    )
    description = models.TextField(
        help_text="Descripción detallada del módulo."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó el módulo."
    )

    def __str__(self):
        return self.name

class Survey(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="Nombre de la encuesta. Máximo 255 caracteres."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Descripción detallada de la encuesta. Opcional."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó la encuesta."
    )

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

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text="Encuesta a la que pertenece esta pregunta."
    )
    text = models.CharField(
        max_length=255,
        help_text="Texto de la pregunta. Máximo 255 caracteres."
    )
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES,
        help_text="Tipo de la pregunta, por ejemplo: 'open', 'closed', etc."
    )
    is_required = models.BooleanField(
        default=False,
        help_text="Indica si la respuesta a esta pregunta es obligatoria."
    )
    data_type = models.CharField(
        max_length=50,
        blank=True, null=True,
        help_text="Tipo de dato esperado, por ejemplo: 'integer', 'string', etc. Opcional."
    )
    min_value = models.IntegerField(
        blank=True, null=True,
        help_text="Valor mínimo permitido para respuestas numéricas. Opcional."
    )
    max_value = models.IntegerField(
        blank=True, null=True,
        help_text="Valor máximo permitido para respuestas numéricas. Opcional."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó la pregunta."
    )

    def __str__(self):
        return self.text

class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        help_text="Pregunta a la que pertenece esta opción."
    )
    text = models.CharField(
        max_length=255,
        help_text="Texto de la opción. Máximo 255 caracteres."
    )
    is_other = models.BooleanField(
        default=False,
        help_text="Indica si esta opción representa la respuesta 'Otro'."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó la opción."
    )


    def __str__(self):
        return self.text

class Response(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Usuario que proporcionó esta respuesta."
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Pregunta a la que corresponde esta respuesta."
    )
    response_text = models.TextField(
        null=True, blank=True,
        help_text="Texto proporcionado como respuesta. Opcional."
    )
    response_number = models.IntegerField(
        null=True, blank=True,
        help_text="Número proporcionado como respuesta. Opcional."
    )
    option_selected = models.ForeignKey(
        'Option',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Opción seleccionada para preguntas cerradas. Opcional."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se registró la respuesta."
    )

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

