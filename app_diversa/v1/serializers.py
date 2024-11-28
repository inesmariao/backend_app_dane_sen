from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..models import Survey, Question, Option, Response

User = get_user_model()



class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    
    # Validar los datos adicionales desde `validation_rules`
    def validate(self, data):
        if data.get('min_value') and not isinstance(data['min_value'], int):
            raise serializers.ValidationError("El valor mínimo debe ser un entero.")
        if data.get('max_value') and not isinstance(data['max_value'], int):
            raise serializers.ValidationError("El valor máximo debe ser un entero.")
        return data

    class Meta:
        model = Question
        fields = '__all__'

class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Survey
        fields = '__all__'

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        survey = Survey.objects.create(**validated_data)
        for question_data in questions_data:
            Question.objects.create(survey=survey, **question_data)
        return survey

class ResponseSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.CharField()
    
    class Meta:
        model = Response
        fields = ['question_id', 'answer', 'user', 'response_text', 'response_number', 'option_selected']
        read_only_fields = ['user', 'response_text', 'response_number', 'option_selected']

    def validate(self, data):
        try:
            question = Question.objects.get(id=data['question_id'])
        except Question.DoesNotExist:
            raise serializers.ValidationError({"question_id": "La pregunta no existe."})

        # Validar según las reglas asociadas a la pregunta
        validation_rules = {
            "data_type": question.data_type,
            "min_value": question.min_value,
            "max_value": question.max_value,
        }
        data_type = validation_rules.get("data_type")

        if data_type == "integer":
            # Validar si la respuesta es un entero
            try:
                answer = int(data['answer'])
            except ValueError:
                raise serializers.ValidationError({"answer": "La respuesta debe ser un número entero."})
            # Validar rangos
            min_value = validation_rules.get("min_value")
            max_value = validation_rules.get("max_value")
            if min_value is not None and answer < min_value:
                raise serializers.ValidationError({"answer": f"El valor debe ser mayor o igual a {min_value}."})
            if max_value is not None and answer > max_value:
                raise serializers.ValidationError({"answer": f"El valor debe ser menor o igual a {max_value}."})
            data['response_number'] = answer

        elif data_type == "text":
            # Validar si la respuesta es un texto
            if not isinstance(data['answer'], str):
                raise serializers.ValidationError({"answer": "La respuesta debe ser un texto."})
            data['response_text'] = data['answer']

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
            option_selected=None  # Para futuras preguntas cerradas
        )