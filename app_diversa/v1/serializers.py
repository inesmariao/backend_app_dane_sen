from rest_framework import serializers
from ..models import Survey, Question, Option, Response, Chapter, SurveyText
from app_geo.serializers import CountrySerializer, DepartmentSerializer, MunicipalitySerializer
from app_geo.models import Country, Department, Municipality

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'option_type', 'is_other', 'note', 'question', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)
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
            'id', 'text', 'instruction', 'is_geographic', 'geography_type',
            'question_type', 'is_required', 'data_type', 'min_value',
            'max_value', 'chapter', 'survey', 'options', 'geography_options', 'created_at', 'updated_at'
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
        instance.text = validated_data.get('text', instance.text)
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
        fields = ['id', 'name', 'description', 'chapters', 'questions', 'texts', 'created_at', 'updated_at']

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
        instance.description = validated_data.get('description', instance.description)
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
    answer = serializers.CharField()

    class Meta:
        model = Response
        fields = ['question_id', 'answer', 'user', 'response_text', 'response_number', 'option_selected', 'country', 'department', 'municipality', 'created_at', 'updated_at']
        read_only_fields = ['user', 'response_text', 'response_number', 'option_selected']

    def validate(self, data):
        try:
            question = Question.objects.get(id=data['question_id'])
        except Question.DoesNotExist:
            raise serializers.ValidationError({"question_id": "La pregunta no existe."})

        # Validar según el tipo de pregunta
        if question.question_type == 'closed':  # Pregunta cerrada
            # Verifica si se ha seleccionado una opción
            option_id = data.get('answer')  # Se asume que `answer` contiene el ID de la opción seleccionada
            if not option_id:
                raise serializers.ValidationError({
                    "answer": "Debe seleccionar una opción para esta pregunta cerrada."
                })
            # Verifica que la opción seleccionada pertenezca a esta pregunta
            if not question.options.filter(id=option_id).exists():
                raise serializers.ValidationError({
                    "answer": "La opción seleccionada no es válida para esta pregunta."
                })

            data['option_selected'] = Option.objects.get(id=option_id)  # Agregar la opción seleccionada

        elif question.question_type == 'open':  # Pregunta abierta
            # Validaciones para preguntas abiertas (entero o texto)
            data_type = question.data_type
            if data_type == "integer":
                try:
                    answer = int(data['answer'])
                except ValueError:
                    raise serializers.ValidationError({"answer": "La respuesta debe ser un número entero."})
                # Validar rangos
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
        user = self.context['request'].user  # Obtener usuario autenticado del contexto
        question = Question.objects.get(id=validated_data['question_id'])

        return Response.objects.create(
            user=user,
            question=question,
            response_text=validated_data.get('response_text'),
            response_number=validated_data.get('response_number'),
            option_selected=validated_data.get('option_selected'),
        )


