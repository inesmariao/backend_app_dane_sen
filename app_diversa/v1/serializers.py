from rest_framework import serializers
from datetime import date, datetime
from ..models import SurveyAttempt, Survey, Question, SubQuestion, Option, Response, Chapter, SurveyText
from app_geo.models import Country, Department, Municipality

class SurveyAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer para los intentos de completar encuestas.
    """
    class Meta:
        model = SurveyAttempt
        fields = '__all__'

    def validate(self, data):
        """
        Validaciones antes de guardar el intento.
        """
        birth_date_str = data.get('birth_date')

        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
            except ValueError:
                raise serializers.ValidationError("Formato de fecha inválido. Debe ser YYYY-MM-DD.")

            today = date.today()

            # No permitir fechas futuras
            if birth_date > today:
                raise serializers.ValidationError("La fecha de nacimiento no puede estar en el futuro.")

            # Verificar mayoría de edad (18+)
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            if age < 18:
                raise serializers.ValidationError("No cumple con el requisito de edad mínima (18 años).")

        return data

class OptionSerializer(serializers.ModelSerializer):
    question_id = serializers.ReadOnlyField(source='question.id')
    subquestion_id = serializers.ReadOnlyField(source='subquestion.id')

    class Meta:
        model = Option
        fields = ['id', 'text_option', 'option_type', 'is_other', 'note', 'order_option', 'question', 'subquestion', 'question_id', 'subquestion_id', 'created_at', 'updated_at']

    def validate(self, data):
        # Validar que una opción esté asociada a una pregunta o subpregunta, pero no a ambas
        if not data.get('question') and not data.get('subquestion'):
            raise serializers.ValidationError("La opción debe estar asociada a una pregunta o a una subpregunta.")
        if data.get('question') and data.get('subquestion'):
            raise serializers.ValidationError("La opción no puede estar asociada tanto a una pregunta como a una subpregunta.")
        return data


class SubQuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    custom_identifier = serializers.CharField(
        required=False, allow_blank=True,
        help_text="Identificador personalizado para subpreguntas. Ejemplo: 17.1"
    )

    is_other = serializers.BooleanField(
        required=False,
        help_text="Indica si esta subpregunta representa la opción 'Otro'."
    )

    class Meta:
        model = SubQuestion
        fields = [
            'id', 'parent_question', 'subquestion_order', 'text_subquestion', 'note',
            'instruction', 'subquestion_type', 'is_required', 'min_value',
            'max_value', 'custom_identifier', 'is_other', 'options', 'created_at', 'updated_at'
        ]

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)
    subquestions = SubQuestionSerializer(many=True, read_only=True)
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all(), required=False)
    geography_options = serializers.SerializerMethodField()

    # Validar los datos adicionales desde `validation_rules`
    def validate(self, data):

        # Validar que min_value y max_value sean enteros si están definidos
        if data.get('min_value') and not isinstance(data['min_value'], int):
            raise serializers.ValidationError("El valor mínimo debe ser un entero.")
        if data.get('max_value') and not isinstance(data['max_value'], int):
            raise serializers.ValidationError("El valor máximo debe ser un entero.")

        # Validar que geography_type solo esté presente en preguntas geográficas
        if not data.get('is_geographic') and data.get('geography_type'):
            raise serializers.ValidationError("Solo las preguntas geográficas pueden tener `geography_type`.")

        # Validar que preguntas de tipo 'birth_date' no tengan geography_type
        if data.get('question_type') == 'birth_date' and data.get('geography_type'):
            raise serializers.ValidationError("Las preguntas de tipo 'Fecha de Nacimiento' no deben tener `geography_type`.")

        return data

    class Meta:
        model = Question
        fields = [
            'id', 'order_question', 'text_question', 'note', 'instruction', 'is_geographic', 'geography_type', 'question_type', 'matrix_layout_type','is_required', 'data_type', 'min_value', 'max_value', 'chapter', 'survey', 'is_multiple', 'options', 'geography_options', 'subquestions', 'created_at', 'updated_at'
        ]

    def validate_question_type(self, value):
        valid_types = ['open', 'closed', 'likert', 'rating', 'matrix', 'birth_date']
        if value not in valid_types:
            raise serializers.ValidationError(f"El tipo de pregunta '{value}' no es válido.")
        return value

    def get_geography_options(self, obj):
        if obj.is_geographic and obj.geography_type:  # Verificar si geography_type no es None
            if obj.geography_type not in ['COUNTRY', 'DEPARTMENT', 'MUNICIPALITY']:
                raise serializers.ValidationError("Tipo de lugar inválido.")

            queryset = None
            if obj.geography_type == 'COUNTRY':
                queryset = Country.objects.all()
            elif obj.geography_type == 'DEPARTMENT':
                queryset = Department.objects.all()
            elif obj.geography_type == 'MUNICIPALITY':
                queryset = Municipality.objects.all()

            return queryset.values('id', 'name')
        return None

    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        question = Question.objects.create(**validated_data)

        for option_data in options_data:
            Option.objects.create(question=question, **option_data)

        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', [])
        instance.text_question = validated_data.get('text_question', instance.text_question)
        instance.is_subquestion = validated_data.get('is_subquestion', instance.is_subquestion)
        instance.parent_order = validated_data.get('parent_order', instance.parent_order)
        instance.question_type = validated_data.get('question_type', instance.question_type)
        instance.save()

        # Actualizar o crear opciones asociadas
        for option_data in options_data:
            option_id = option_data.get('id')
            if option_id:
                option = Option.objects.get(id=option_id, question=instance)
                for attr, value in option_data.items():
                    setattr(option, attr, value)
                option.save()
            else:
                Option.objects.create(question=instance, **option_data)

        return instance

class ChapterSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'name', 'description', 'survey', 'questions', 'created_at', 'updated_at']

class SurveyTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyText
        fields = ['id', 'survey', 'title', 'description', 'is_active', 'created_at', 'updated_at']

class SurveySerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, required=False)
    questions = QuestionSerializer(many=True, required=False)
    texts = SurveyTextSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description_name', 'title', 'description_title', 'chapters', 'questions', 'texts', 'created_at', 'updated_at']

    def create(self, validated_data):
        chapters_data = validated_data.pop('chapters', [])
        questions_data = validated_data.pop('questions', [])
        texts_data = validated_data.pop('texts', [])
        survey = Survey.objects.create(**validated_data)

        # Crear capítulos asociados
        for chapter_data in chapters_data:
            Chapter.objects.create(survey=survey, **chapter_data)

        # Crear preguntas asociadas
        for question_data in questions_data:
            Question.objects.create(survey=survey, **question_data)

        # Crear textos asociados
        for text_data in texts_data:
            SurveyText.objects.create(survey=survey, **text_data)

        return survey

    def validate(self, data):
        chapters = data.get('chapters', [])
        questions = data.get('questions', [])

        # Validar que las preguntas no pertenezcan a capítulos inexistentes
        for question in questions:
            if question.get('chapter') and question['chapter'] not in [chapter['id'] for chapter in chapters]:
                raise serializers.ValidationError("Las preguntas deben pertenecer a capítulos existentes en la encuesta.")

        return data

    def update(self, instance, validated_data):
        chapters_data = validated_data.pop('chapters', [])
        questions_data = validated_data.pop('questions', [])
        texts_data = validated_data.pop('texts', [])
        instance.name = validated_data.get('name', instance.name)
        instance.title = validated_data.get('title', instance.title)
        instance.description_title = validated_data.get('description_title', instance.description_title)
        instance.description_name = validated_data.get('description_name', instance.description_name)
        instance.save()

        # Actualizar o crear capítulos
        for chapter_data in chapters_data:
            chapter_id = chapter_data.get('id')
            if chapter_id:
                chapter = Chapter.objects.get(id=chapter_id, survey=instance)
                for attr, value in chapter_data.items():
                    setattr(chapter, attr, value)
                chapter.save()
            else:
                Chapter.objects.create(survey=instance, **chapter_data)

        # Actualizar o crear preguntas
        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id:
                question = Question.objects.get(id=question_id, survey=instance)
                for attr, value in question_data.items():
                    setattr(question, attr, value)
                question.save()
            else:
                Question.objects.create(survey=instance, **question_data)

        # Actualizar textos
        for text_data in texts_data:
            text_id = text_data.get('id')
            if text_id:
                text = SurveyText.objects.get(id=text_id, survey=instance)
                for attr, value in text_data.items():
                    setattr(text, attr, value)
                text.save()
            else:
                SurveyText.objects.create(survey=instance, **text_data)

        return instance

class ResponseSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(help_text="ID de la pregunta a la que corresponde la respuesta.")
    subquestion_id = serializers.PrimaryKeyRelatedField(
        queryset=SubQuestion.objects.all(), allow_null=True, required=False,
        write_only=True,
        help_text="ID de la subpregunta asociada (solo para preguntas tipo matriz)."
    )
    subquestion = serializers.PrimaryKeyRelatedField(
        queryset=SubQuestion.objects.all(), allow_null=True, required=False,
        help_text="Objeto de la subpregunta asociada.", write_only=True
    )
    answer = serializers.CharField(required=False, allow_blank=True, help_text="Texto ingresado en una pregunta abierta.")
    option_selected = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(), allow_null=True, required=False,
        help_text="Opción seleccionada en preguntas cerradas."
    )
    options_multiple_selected = serializers.PrimaryKeyRelatedField(many=True, queryset=Option.objects.all(), required=False)
    survey_attempt = serializers.PrimaryKeyRelatedField(
        queryset=SurveyAttempt.objects.all(), required=False,
        help_text="Intento de la encuesta asociado a esta respuesta."
    )
    other_text = serializers.CharField(required=False, allow_blank=True, help_text="Texto ingresado por el usuario cuando selecciona la opción 'Otro'.")

    # Campos geográficos
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), allow_null=True, required=False)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), allow_null=True, required=False)
    municipality = serializers.PrimaryKeyRelatedField(queryset=Municipality.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Response
        fields = [
            "question_id", "subquestion_id", "subquestion", "answer", "option_selected",
            "options_multiple_selected", 'response_text', "survey_attempt", "country",
            "department", "municipality", "other_text"
        ]

    def validate_subquestion_id(self, value):
        """Valida que subquestion_id sea un número entero y no un objeto SubQuestion"""

        if isinstance(value, SubQuestion):
            return value.id
        elif not isinstance(value, int):
            raise serializers.ValidationError("subquestion_id debe ser un número entero")
        return value

    def validate(self, data):
        """
        Validación de los datos antes de guardar la respuesta.
        """

        question_id = data.get("question_id")
        subquestion_id = data.pop("subquestion_id", None)

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise serializers.ValidationError({"question_id": f"ID de pregunta inválido: {question_id} no existe."})

        # Convertimos `subquestion_id` en `subquestion`
        if subquestion_id:
            subquestion = SubQuestion.objects.filter(id=subquestion_id).first()
            if not subquestion:
                raise serializers.ValidationError({"subquestion_id": f"La subpregunta con ID {subquestion_id} no existe."})
            data["subquestion"] = subquestion  # Guardamos la subpregunta en `data`

        # Validación de preguntas tipo matriz
        if question.question_type == 'matrix' and not data.get("subquestion"):
            raise serializers.ValidationError({"subquestion_id": "Las preguntas tipo matriz requieren una subpregunta asociada."})

        # Si la pregunta es de selección múltiple, `options_multiple_selected` debe tener datos
        if question.is_multiple and not data.get("options_multiple_selected"):
            raise serializers.ValidationError("Debe seleccionar al menos una opción en preguntas de selección múltiple.")

        # Validar que al menos una respuesta sea proporcionada
        if not data.get("answer") and not data.get("option_selected") and not data.get("options_multiple_selected"):
            # excepción: si la subpregunta es 'is_other' y hay other_text
            subq = data.get("subquestion")
            if not (subq and subq.is_other and data.get("other_text")):
                raise serializers.ValidationError("Debe proporcionar una respuesta válida: texto, número o seleccionar una opción.")

        # Validación de opciones is_other
        option = data.get("option_selected")
        other_text = data.get("other_text")

        if option:
            if option.is_other and not other_text:
                raise serializers.ValidationError(
                    {"other_text": "Debe proporcionar un valor si selecciona la opción 'Otro'."}
                )

        # Validación de subpregunta is_other
        subquestion = data.get("subquestion_id")
        if subquestion and subquestion.is_other and not data.get("other_text"):
            raise serializers.ValidationError({"other_text": "Debe proporcionar un texto para la subpregunta 'Otro'."})

        if question.question_type == 'birth_date':
            if not data.get('response_number'):
                raise serializers.ValidationError("Debe seleccionar una fecha de nacimiento válida.")

        # Validación para preguntas geográficas
        if question.is_geographic and question.id != 8:
            if not data.get("department"):
                raise serializers.ValidationError({"department": "Debe seleccionar un departamento."})
            if not data.get("municipality"):
                raise serializers.ValidationError({"municipality": "Debe seleccionar un municipio."})

        # Validación de `option_selected` antes de acceder a sus propiedades
        option = data.get('option_selected')
        if option:
            # Validación de opciones geográficas
            if option.option_type == 'COUNTRY' and not data.get('country'):
                raise serializers.ValidationError({"country": "Debe seleccionar un país."})
            elif option.option_type == 'DEPARTMENT' and not data.get('department'):
                raise serializers.ValidationError({"department": "Debe seleccionar un departamento."})
            elif option.option_type == 'MUNICIPALITY' and not data.get('municipality'):
                raise serializers.ValidationError({"municipality": "Debe seleccionar un municipio."})

        # Validación específica para Colombia
        if data.get("country") and data["country"].numeric_code == 170:  # Colombia
            if option and option.option_type != 'COUNTRY':
                if not data.get("department"):
                    raise serializers.ValidationError({"department": "Debe seleccionar un departamento para Colombia."})
                if not data.get("municipality"):
                    raise serializers.ValidationError({"municipality": "Debe seleccionar un municipio para Colombia."})

        # Validar selección múltiple
        if "options_multiple_selected" in data:
            option_ids = data["options_multiple_selected"]

            if not all(isinstance(opt, Option) for opt in option_ids):
                raise serializers.ValidationError({"options_multiple_selected": "Debe contener objetos Option válidos."})

        return data

    def create(self, validated_data):
        """
        Creación de la respuesta asegurando que se asocie a un `survey_attempt`.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        else:
            raise serializers.ValidationError({"user": "El usuario es obligatorio."})
    
        # Extraer y procesar las opciones múltiples seleccionadas
        options_multiple_selected = validated_data.pop('options_multiple_selected', [])

        # Extraer subpregunta correctamente
        subquestion = validated_data.pop('subquestion', None)

        # Crear la instancia de Response
        response = Response.objects.create(
            **validated_data,
            subquestion=subquestion
        )

        # Asignar opciones múltiples seleccionadas si existen
        if options_multiple_selected:
            response.options_multiple_selected.set(options_multiple_selected)

        return response
