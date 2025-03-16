from rest_framework import serializers
from ..models import SurveyAttempt, Survey, Question, SubQuestion, Option, Response, Chapter, SurveyText
from app_geo.models import Country, Department, Municipality
import logging # Debug

logger = logging.getLogger(__name__) # Debug

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
        if data.get('birth_year') and (data.get('birth_month') is None or data.get('birth_day') is None):
            raise serializers.ValidationError("Si proporciona el año de nacimiento, también debe indicar el mes y el día.")

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
    class Meta:
        model = SubQuestion
        fields = [
            'id', 'parent_question', 'subquestion_order', 'text_subquestion', 'note',
            'instruction', 'subquestion_type', 'is_required', 'min_value',
            'max_value', 'custom_identifier', 'options', 'created_at', 'updated_at'
        ]

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)
    subquestions = SubQuestionSerializer(many=True, read_only=True)
    chapter = serializers.PrimaryKeyRelatedField(queryset=Chapter.objects.all(), required=False)
    geography_options = serializers.SerializerMethodField()

    # Validar los datos adicionales desde `validation_rules`
    def validate(self, data):
        if data.get('min_value') and not isinstance(data['min_value'], int):
            raise serializers.ValidationError("El valor mínimo debe ser un entero.")
        if data.get('max_value') and not isinstance(data['max_value'], int):
            raise serializers.ValidationError("El valor máximo debe ser un entero.")
        return data

    class Meta:
        model = Question
        fields = [
            'id', 'order_question', 'text_question', 'note', 'instruction', 'is_geographic', 'geography_type', 'question_type', 'matrix_layout_type','is_required', 'data_type', 'min_value', 'max_value', 'chapter', 'survey', 'is_multiple', 'options', 'geography_options', 'subquestions', 'created_at', 'updated_at'
        ]

    def get_geography_options(self, obj):
        if obj.is_geographic:
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
    answer = serializers.CharField(required=False, allow_blank=True, help_text="Texto ingresado en una pregunta abierta.")
    option_selected = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(), allow_null=True, required=False,
        help_text="Opción seleccionada en preguntas cerradas."
    )
    options_multiple_selected = serializers.ListField(
        child=serializers.IntegerField(), allow_null=True, allow_empty=True, required=False,
        help_text="Lista de opciones seleccionadas en preguntas de selección múltiple."
    )
    survey_attempt = serializers.PrimaryKeyRelatedField(
        queryset=SurveyAttempt.objects.all(), required=False,
        help_text="Intento de la encuesta asociado a esta respuesta."
    )

    # Campos geográficos
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), allow_null=True, required=False)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), allow_null=True, required=False)
    municipality = serializers.PrimaryKeyRelatedField(queryset=Municipality.objects.all(), allow_null=True, required=False)
    new_department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), allow_null=True, required=False)
    new_municipality = serializers.PrimaryKeyRelatedField(queryset=Municipality.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Response
        fields = [
            "question_id", "answer", "option_selected", "options_multiple_selected",
            "survey_attempt", "country", "department", "municipality",
            "new_department", "new_municipality"
        ]

    def validate(self, data):
        """
        Validación de los datos antes de guardar la respuesta.
        """
        try:
            question = Question.objects.get(id=data['question_id'])
        except Question.DoesNotExist:
            raise serializers.ValidationError({"question_id": f"ID inválido: {data['question_id']} no existe."})

        # Si la pregunta NO es geográfica, no necesita validación extra
        if not question.is_geographic:
            return data
        
        option = data.get('option_selected')
        
        # Validación para preguntas geográficas:
        if not option:
            raise serializers.ValidationError({"option_selected": "Debe seleccionar una opción para preguntas geográficas."})

        if option.text_option.strip().lower() == "no":
            data['country'] = None
            data['department'] = None
            data['municipality'] = None
            return data
        
        # Caso especial: Pregunta 7
        if data['question_id'] == 7 and option.text_option.strip().lower() == "sí":
            if not data.get('new_department'):
                raise serializers.ValidationError({"new_department": "Debe seleccionar un nuevo departamento."})
            if not data.get('new_municipality'):
                raise serializers.ValidationError({"new_municipality": "Debe seleccionar un nuevo municipio."})
            return data

        # Validación para las demás preguntas geográficas:
        if option.option_type == 'COUNTRY' and not data.get('country'):
            raise serializers.ValidationError({"country": "Debe seleccionar un país."})
        elif option.option_type == 'DEPARTMENT' and not data.get('department'):
            raise serializers.ValidationError({"department": "Debe seleccionar un departamento."})
        elif option.option_type == 'MUNICIPALITY' and not data.get('municipality'):
            raise serializers.ValidationError({"municipality": "Debe seleccionar un municipio."})


        if 'country' in data and data['country'] and data['country'].numeric_code == 170:  # Colombia
            if option.option_type != 'COUNTRY':
                if 'department' not in data or data['department'] is None:
                    raise serializers.ValidationError({"department": "Debe seleccionar un departamento para Colombia."})
                if 'municipality' not in data or data['municipality'] is None:
                    raise serializers.ValidationError({"municipality": "Debe seleccionar un municipio para Colombia."})

        if 'options_multiple_selected' in data and data['options_multiple_selected']:
            for option_id in data['options_multiple_selected']:
                if not Option.objects.filter(id=option_id).exists():
                    raise serializers.ValidationError(f"La opción con ID {option_id} no existe.")

        return data

    def create(self, validated_data):
        """
        Creación de la respuesta asegurando que se asocie a un `survey_attempt`.
        """
        user = self.context['request'].user
        question = Question.objects.get(id=validated_data['question_id'])

        # Si la pregunta es la 8 y la opción es "Sí", usar `new_department` y `new_municipality`
        if question.id == 8 and validated_data.get('option_selected') and validated_data['option_selected'].text_option.strip().lower() == "sí":
            department = validated_data.get('new_department')
            municipality = validated_data.get('new_municipality')
        else:
            # Para otras preguntas, usar los campos normales
            department = validated_data.get('department')
            municipality = validated_data.get('municipality')

        # Extraer instancias de los campos relacionados
        country = validated_data.pop('country', None)

        # Crear la respuesta usando los IDs
        response = Response.objects.create(
            user=user,
            question=question,
            survey_attempt=validated_data.get("survey_attempt"),
            country=validated_data.get('country'),
            department=department,
            municipality=municipality,
            response_text=validated_data.get('answer') if isinstance(validated_data.get('answer'), str) else None,
            response_number=validated_data.get('answer') if isinstance(validated_data.get('answer'), int) else None,
            option_selected=validated_data.get('option_selected'),
            options_multiple_selected=validated_data.get('options_multiple_selected', [])
        )

        return response
