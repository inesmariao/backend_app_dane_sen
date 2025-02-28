from django.db import models
from app_geo.models import Country, Department, Municipality
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import JSONField

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
    
    MATRIX_LAYOUT_CHOICES = [
        ('row', 'Matriz - Fila'),
        ('column', 'Matriz - Columna')
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
    order_question = models.PositiveIntegerField(
        default=0,
        help_text="Orden de la pregunta dentro de la encuesta."
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
    matrix_layout_type = models.CharField(
        max_length=10,
        choices=MATRIX_LAYOUT_CHOICES,
        blank=True,
        null=True,
        help_text="Diseño para preguntas tipo matriz: 'Fila' (row) u 'Columna' (column)."
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

    @property
    def subquestions_list(self):
        return self.subquestions.all().order_by('subquestion_order')

    def __str__(self):
        return f"{self.order_question} - {self.text_question}"

class SubQuestion(models.Model):
    id = models.IntegerField(primary_key=True)
    parent_question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='subquestions',
        help_text="Pregunta principal a la que pertenece esta subpregunta."
    )
    custom_identifier = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        help_text="Identificador personalizado para la subpregunta, como 17.1 o 18.2. Opcional, pero único si se usa."
    )
    subquestion_order = models.PositiveIntegerField(
        default=0,
        help_text="Orden de la subpregunta dentro de la pregunta principal."
    )
    text_subquestion = models.CharField(
        max_length=255,
        help_text="Texto de la subpregunta. Máximo 255 caracteres."
    )
    instruction = models.TextField(
        blank=True, null=True,
        help_text="Instrucción específica para la subpregunta. Opcional."
    )
    subquestion_type = models.CharField(
        max_length=10,
        choices=[
            ('open', 'Pregunta Abierta'),
            ('closed', 'Pregunta Cerrada'),
            ('likert', 'Escala Likert'),
            ('rating', 'Escala de Puntuación'),
        ],
        help_text="Tipo de la subpregunta, por ejemplo: 'open', 'closed', etc."
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
        help_text="Indica si la subpregunta permite seleccionar múltiples opciones."
    )
    is_required = models.BooleanField(
        default=False,
        help_text="Indica si la respuesta a esta subpregunta es obligatoria."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se creó la subpregunta."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha y hora en que se actualizó la subpregunta."
    )

    def clean(self):
        # Validar que las subpreguntas solo pueden estar asociadas a preguntas tipo 'matrix'
        if self.parent_question and self.parent_question.question_type != 'matrix':
            raise ValidationError("Las subpreguntas solo pueden estar asociadas a preguntas de tipo 'matrix'.")

        # Asegurar que los identificadores personalizados sean únicos dentro de las subpreguntas de una misma pregunta principal.
        if self.custom_identifier:
            if self.parent_question and self.parent_question.pk:
                siblings = SubQuestion.objects.filter(parent_question=self.parent_question)
                if siblings.exclude(id=self.id).filter(custom_identifier=self.custom_identifier).exists():
                    raise ValidationError(
                        f"El identificador personalizado '{self.custom_identifier}' ya está en uso dentro de esta pregunta principal."
                    )
            else:
                raise ValidationError("La pregunta principal debe estar guardada antes de añadir subpreguntas.")

        super().clean()

    def __str__(self):
        if self.custom_identifier:
            return f"{self.custom_identifier} - {self.text_subquestion}"
        return f"{self.subquestion_order} - {self.text_subquestion}"


class Option(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
        blank=True,
        null=True,
        help_text="Pregunta a la que pertenece esta opción. Dejar en blanco si pertenece a una subpregunta."
    )
    subquestion = models.ForeignKey(
        SubQuestion,
        on_delete=models.CASCADE,
        related_name='options',
        blank=True,
        null=True,
        help_text="Subpregunta a la que pertenece esta opción. Dejar en blanco si pertenece a una pregunta."
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
        blank=True,
        null=True,
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
        auto_now=True,
        help_text="Fecha y hora en que se actualizó la opción."
    )

    @property
    def question_id(self):
        return self.question.id if self.question else None

    @property
    def subquestion_id(self):
        return self.subquestion.id if self.subquestion else None

    def clean(self):
        """
        Valida las reglas específicas para las asociaciones entre opciones,
        preguntas y subpreguntas.
        """
        # Validar que al menos uno de los campos (question o subquestion) esté definido.
        if not self.question and not self.subquestion:
            raise ValidationError("La opción debe estar asociada a una pregunta o a una subpregunta.")

        # Permitir que una opción esté asociada a ambos campos al mismo tiempo.
        if self.question and self.subquestion:
            # Validación adicional para evitar inconsistencias.
            if self.question.id != self.subquestion.parent_question_id:
                raise ValidationError("La pregunta y la subpregunta deben estar relacionadas.")

        # Validar el texto de la opción si se marca como 'Otro'
        if self.is_other and not self.text_option.lower() == "otro":
            raise ValidationError("Si la opción es marcada como 'Otro', el texto debe ser 'Otro'.")


    def __str__(self):
        """
        Representa el texto de la opción, indicando si pertenece a una pregunta o subpregunta.
        """
        if self.question and self.subquestion:
            return f"[Q-{self.question.id} | SQ-{self.subquestion.id}] {self.text_option}"
        elif self.question:
            return f"[Q-{self.question.id}] {self.text_option}"
        elif self.subquestion:
            return f"[SQ-{self.subquestion.id}] {self.text_option}"
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
    # Campos para la pregunta 7
    new_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='responses_new_departments',
        help_text="Nuevo departamento seleccionado (pregunta 7)."
    )
    new_municipality = models.ForeignKey(
        Municipality,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='responses_new_municipalities',
        help_text="Nuevo municipio seleccionado (pregunta 7)."
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
    options_multiple_selected = JSONField(
        null=True, blank=True,
        help_text="Opciones seleccionadas para preguntas de selección múltiple (almacenadas como JSON)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en que se registró la respuesta."
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha y hora en que se actualizó la respuesta."
    )
    
    @property
    def country_code(self):
        return self.country.numeric_code if self.country else None

    @property
    def department_code(self):
        return self.department.code if self.department else None

    @property
    def municipality_code(self):
        return self.municipality.code if self.municipality else None

    def __str__(self):
        return f"Respuesta de {self.user} a {self.question.text_question}"

    def clean(self):
        """
        Validaciones personalizadas para asegurar que las respuestas cumplan con los requisitos según el tipo de pregunta.
        """
        if self.response_number is not None and self.response_text is not None:
            raise ValidationError("No se puede proporcionar una respuesta en `response_text` y `response_number` al mismo tiempo.")
        
        if self.question.question_type == 'open':
            if self.response_number is None and self.response_text is None:
                raise ValidationError("Debe proporcionar una respuesta abierta (texto o número).")

        elif self.question.question_type == 'closed' and not self.question.is_multiple:
            if not self.option_selected:
                raise ValidationError("Debe seleccionar una opción para una pregunta cerrada.")

        elif self.question.question_type == 'closed' and self.question.is_multiple:
            if not self.options_multiple_selected:
                raise ValidationError("Debe seleccionar al menos una opción para una pregunta de selección múltiple.")
            
            # Validación del tipo de datos
            if self.options_multiple_selected is not None:
                if not isinstance(self.options_multiple_selected, list):
                    raise ValidationError("El campo `options_multiple_selected` debe ser una lista de opciones seleccionadas.")
                if not all(isinstance(option, int) for option in self.options_multiple_selected):
                    raise ValidationError("Todas las opciones seleccionadas deben ser IDs enteros.")

        super().clean()

    def save(self, *args, **kwargs):
        """
        Refuerzo de validación en `save()`, asegurando que no se guarden `response_text` y `response_number` al mismo tiempo.
        """
        self.clean()
        super().save(*args, **kwargs)


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
