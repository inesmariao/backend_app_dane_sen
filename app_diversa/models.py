from django.db import models
from app_geo.models import Country, Department, Municipality
from django.conf import settings
from django.core.exceptions import ValidationError

class Survey(models.Model):
    name = models.CharField(
        max_length=255,
        help_text="Nombre de la encuesta, se muestra en el encabezado de la encuesta. Máximo 255 caracteres."
    )
    description_name = models.TextField(
        blank=True, null=True,
        help_text="Descripción detallada de la encuesta, se muestra debajo del name en el encabezado de la encuesta. Opcional."
    )
    title = models.CharField(
        max_length=255,
        help_text="Título de la encuesta que se muestra en las cards del índice. Obligatorio.",
        default="TÍTULO POR DEFECTO"
    )
    description_title = models.TextField(
        blank=True, null=True,
        help_text="Descripción del título de la encuesta que se muestra en las cards del índice."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó la encuesta."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora en que se actualizó la encuesta."
    )

    def save(self, *args, **kwargs):
        # Convertir a mayúsculas antes de guardar
        if self.name:
            self.name = self.name.upper()
        if self.title:
            self.title = self.title.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Chapter(models.Model):
    survey = models.ForeignKey(
        Survey, on_delete=models.CASCADE, related_name='chapters', help_text="Encuesta a la que pertenece este capítulo."
    )
    name = models.CharField(
        max_length=255, help_text="Nombre del capítulo."
    )
    description = models.TextField(
        blank=True, null=True, help_text="Descripción opcional del capítulo."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Fecha de creación del capítulo."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora en que se actualizó el capítulo."
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
    chapter = models.ForeignKey(
        'Chapter', on_delete=models.SET_NULL, null=True, blank=True, related_name='questions',
        help_text="Capítulo al que pertenece esta pregunta. Puede ser nulo si no está asociado a un capítulo."
    )
    parent_question = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subquestions',
        help_text="Pregunta padre para subpreguntas en una matriz."
    )
    order_question = models.PositiveIntegerField(
        default=0,
        help_text="Orden de la pregunta dentro de la encuesta."
    )
    subquestion_order = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Orden de la subpregunta dentro de una matriz."
    )
    text_question = models.CharField(
        max_length=255,
        help_text="Texto de la pregunta. Máximo 255 caracteres."
    )
    instruction = models.TextField(
        blank=True, null=True,
        help_text="Instrucción para el usuario sobre cómo responder la pregunta. Opcional."
    )
    is_geographic = models.BooleanField(
        default=False,
        help_text="Indica si la pregunta requiere selección geográfica."
    )
    geography_type = models.CharField(
        max_length=20,
        choices=[('COUNTRY', 'País'), ('DEPARTMENT', 'Departamento'), ('MUNICIPALITY', 'Municipio')],
        blank=True, null=True,
        help_text="Especifica el nivel geográfico (país, departamento o municipio)."
    )
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPES,
        help_text="Tipo de la pregunta, por ejemplo: 'open', 'closed', etc."
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
    is_multiple = models.BooleanField(
        default=False,
        help_text="Indica si la pregunta permite seleccionar múltiples opciones."
    )
    is_required = models.BooleanField(
        default=False,
        help_text="Indica si la respuesta a esta pregunta es obligatoria."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó la pregunta."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora en que se actualizó la pregunta."
    )

    def clean(self):
        # Validar que las subpreguntas solo pueden estar asociadas a preguntas tipo 'matrix'
        if self.parent_question and self.parent_question.question_type != 'matrix':
            raise ValidationError("Las subpreguntas solo pueden estar asociadas a preguntas de tipo 'matrix'.")
        super().clean()

    @property
    def subquestions_list(self):
        return self.subquestions.all().order_by('subquestion_order')

    def __str__(self):
        return self.text_question


class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        help_text="Pregunta a la que pertenece esta opción."
    )
    option_type = models.CharField(
        max_length=20,
        choices=[('COUNTRY', 'País'), ('DEPARTMENT', 'Departamento'), ('MUNICIPALITY', 'Municipio')],
        blank=True, null=True,
        help_text="Especifica el tipo de esta opción."
    )
    text_option = models.CharField(
        max_length=255,
        help_text="Texto de la opción. Máximo 255 caracteres."
    )
    is_other = models.BooleanField(
        default=False,
        help_text="Indica si esta opción representa la respuesta 'Otro'."
    )
    note = models.TextField(
        blank=True, null=True,
        help_text="Nota aclaratoria para esta opción. Opcional."
    )
    order_option = models.PositiveIntegerField(
        default=0,
        help_text="Orden de la opción."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó la opción."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora en que se actualizó la opción."
    )

    def __str__(self):
        return self.text_option


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
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        help_text="País seleccionado."
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        help_text="Departamento seleccionado."
    )
    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        help_text="Municipio seleccionado."
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
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora en que se actualizó la respuesta."
    )

    def __str__(self):
        return f"Respuesta de {self.user} a {self.question.text_question}"

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

class SurveyText(models.Model):
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='texts',
        help_text="Survey to which this text belongs."
    )
    title = models.CharField(
        max_length=255,
        help_text="Title of the survey text."
    )
    description = models.TextField(
        blank=True, null=True,
        help_text="Description of the survey text."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if this text is active."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the text was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora en que se actualizó el texto."
    )

    def __str__(self):
        return self.title
