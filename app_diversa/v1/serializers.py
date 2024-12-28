from rest_framework import serializers
from ..models import Survey, Question, SubQuestion, Option, Response, Chapter, SurveyText
from app_geo.models import Country, Department, Municipality

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
            'id', 'parent_question', 'subquestion_order', 'text_subquestion',
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
            'id', 'order_question', 'text_question', 'instruction', 'is_geographic', 'geography_type', 'question_type', 'matrix_layout_type','is_required', 'data_type', 'min_value', 'max_value', 'chapter', 'survey', 'is_multiple', 'options', 'geography_options', 'subquestions', 'created_at', 'updated_at'
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
    question_id = serializers.IntegerField()
    answer = serializers.CharField(allow_null=True)
    options_multiple_selected = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, required=False
    )

    class Meta:
        model = Response
        fields = ['question_id', 'answer', 'user', 'response_text', 'response_number', 'option_selected', 'options_multiple_selected', 'country', 'department', 'municipality', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        try:
            question = Question.objects.get(id=data['question_id'])
        except Question.DoesNotExist:
            raise serializers.ValidationError({"question_id": "La pregunta no existe."})

        # Validar preguntas cerradas no múltiples
        if not question.is_multiple and not data.get('option_selected'):
            raise serializers.ValidationError({"option_selected": "Debe seleccionar una opción para esta pregunta."})

        # Validar preguntas de selección múltiple
        if question.is_multiple:
            if 'options_multiple_selected' not in data or not data['options_multiple_selected']:
                raise serializers.ValidationError({
                    "options_multiple_selected": "Debe seleccionar al menos una opción para preguntas de selección múltiple."
                })
            # Validar que todas las opciones seleccionadas pertenezcan a la pregunta
            options = Option.objects.filter(question=question).values_list('id', flat=True)
            invalid_options = [opt for opt in data['options_multiple_selected'] if opt not in options]
            if invalid_options:
                raise serializers.ValidationError({
                    "options_multiple_selected": f"Las siguientes opciones no son válidas: {invalid_options}"
                })

        # Convertir answer a un entero si la pregunta es geográfica:
        if question.is_geographic and question.geography_type == "DEPARTMENT":
            try:
                data['answer'] = int(data['answer'])  # Convertir el valor a entero
            except (TypeError, ValueError):
                raise serializers.ValidationError({"answer": "El código del departamento debe ser un número entero."})

        # Validación para preguntas cerradas
        if question.question_type == 'closed':  # Pregunta cerrada
            if data.get('answer') is None:
                raise serializers.ValidationError({"option_selected": "Debe seleccionar una opción."})
            option = Option.objects.filter(id=data['answer'], question=question).first()
            if not option:
                raise serializers.ValidationError({"answer": "La opción seleccionada no es válida para esta pregunta."})
            data['option_selected'] = option

        # Validaciones para preguntas abiertas
        elif question.question_type == 'open':
            data_type = question.data_type
            if data.get('answer') is None:
                raise serializers.ValidationError({"answer": "Este campo no puede estar vacío."})
            if data_type == "integer":
                try:
                    answer = int(data['answer'])
                except ValueError:
                    raise serializers.ValidationError({"answer": "La respuesta debe ser un número entero."})
                if question.min_value is not None and answer < question.min_value:
                    raise serializers.ValidationError({"answer": f"El valor debe ser mayor o igual a {question.min_value}."})
                if question.max_value is not None and answer > question.max_value:
                    raise serializers.ValidationError({"answer": f"El valor debe ser menor o igual a {question.max_value}."})
                data['response_number'] = answer
            elif data_type == "text":
                if not isinstance(data['answer'], str):
                    raise serializers.ValidationError({"answer": "La respuesta debe ser un texto."})
                data['response_text'] = data['answer']

        else:
            raise serializers.ValidationError({
                "question_type": f"El tipo de pregunta '{question.question_type}' no está soportado."
            })

        return data


    def create(self, validated_data):
        """
        Crea una respuesta en la base de datos, asociando al usuario autenticado y validando la pregunta.
        """
        user = self.context['request'].user
        question = Question.objects.get(id=validated_data['question_id'])
        response = Response.objects.create(
            user=user,
            question=question,
            response_text=validated_data.get('response_text'),
            response_number=validated_data.get('response_number'),
            option_selected=validated_data.get('option_selected'),
            options_multiple_selected=validated_data.get('options_multiple_selected'),
        )
        return response


