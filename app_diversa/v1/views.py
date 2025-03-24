from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response as DRFResponse
from rest_framework.serializers import ValidationError as DRFValidationError
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import SurveyAttempt, Survey, Question, SubQuestion, Option, Chapter, SurveyText, SystemMessage
from ..models import Response as ModelResponse
from .serializers import SurveyAttemptSerializer, SurveySerializer, QuestionSerializer, SubQuestionSerializer, OptionSerializer, ResponseSerializer, ChapterSerializer, SurveyTextSerializer
from app_geo.models import Country, Department, Municipality
import tablib
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from datetime import date, datetime


@api_view(['GET'])
@permission_classes([AllowAny])
def get_message_by_key(request, key):
    try:
        message = SystemMessage.objects.get(key=key, is_active=True)
        return Response({
            "title": message.title,
            "content": message.content
        })
    except SystemMessage.DoesNotExist:
        return Response({"error": "Mensaje no encontrado."}, status=404)


class WelcomeView(APIView):
    """
    Vista de bienvenida para usuarios autenticados.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Mensaje de bienvenida para usuarios autenticados.",
        responses={200: openapi.Response(description="Mensaje de bienvenida")}
    )
    def get(self, request):
        return Response({"message": "Bienvenido/a a AppDiversa"})


class SurveyAttemptViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar intentos de completar encuestas (SurveyAttempt).
    """
    queryset = SurveyAttempt.objects.all()
    serializer_class = SurveyAttemptSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Lista de intentos de completar encuestas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea un nuevo intento de encuesta.")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Verificación de edad
        birth_year = serializer.validated_data.get('birth_year')
        birth_month = serializer.validated_data.get('birth_month')
        birth_day = serializer.validated_data.get('birth_day')

        if birth_year and birth_month and birth_day:
            try:
                birth_date = date(birth_year, birth_month, birth_day)
                today = date.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

                if age < 18:
                    return Response(
                        {"message": {"message": "Agradecemos su interés en participar en esta encuesta. Sin embargo, no cumple con el perfil, ya que la encuesta está dirigida a personas mayores de 18 años que residan en Colombia en los últimos 5 años."},
},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ValueError:
                return Response({"message": "Fecha de nacimiento inválida."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Obtiene un intento de encuesta específico por su ID.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Actualiza un intento de encuesta existente.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Elimina un intento de encuesta.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class SurveyViewSet(viewsets.ModelViewSet):
    """
    CRUD para encuestas (surveys).
    """
    queryset = Survey.objects.all().order_by('-created_at')
    serializer_class = SurveySerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_description="Lista de todas las encuestas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea una nueva encuesta.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Obtiene una encuesta específica por su ID.")
    def retrieve(self, request, *args, **kwargs):
        survey = self.get_object()
        serializer = self.get_serializer(survey)
        data = serializer.data
        data['questions'] = sorted(
            data['questions'], key=lambda q: q['order_question'])
        return Response(data)

    @swagger_auto_schema(operation_description="Actualiza una encuesta existente.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Elimina una encuesta específica.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Listar todas las encuestas disponibles.
        """
        return super().list(request, *args, **kwargs)


class ChapterViewSet(viewsets.ModelViewSet):
    """
    ViewSet para realizar operaciones CRUD sobre Chapter.
    """
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


class SubQuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD para subpreguntas (SubQuestion).
    """
    queryset = SubQuestion.objects.prefetch_related('options').all()
    serializer_class = SubQuestionSerializer

    @swagger_auto_schema(operation_description="Cuando se crea una subpregunta, se almacena el valor de is_other.")
    def perform_create(self, serializer):
        """
        Agregar soporte para `is_other` al crear una subpregunta.
        """
        is_other = self.request.data.get("is_other", False)
        serializer.save(is_other=is_other)

    @swagger_auto_schema(operation_description="Cuando se actualiza una subpregunta, también se puede modificar el valor de is_other.")
    def perform_update(self, serializer):
        """
        Agregar soporte para actualizar `is_other` en una subpregunta.
        """
        is_other = self.request.data.get("is_other", False)
        serializer.save(is_other=is_other)

    @swagger_auto_schema(operation_description="Lista de todas las subpreguntas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea una nueva subpregunta.")
    def create(self, request, *args, **kwargs):
        data = request.data
        parent_question_id = data.get('parent_question')
        custom_identifier = data.get('custom_identifier')

        # Validar que la pregunta padre exista y sea de tipo 'matrix'
        if parent_question_id:
            parent_question = Question.objects.filter(
                id=parent_question_id).first()
            if not parent_question:
                raise DRFValidationError(
                    {"error": "La pregunta padre no existe."})
            if parent_question.question_type != "matrix":
                raise DRFValidationError(
                    {"error": "Solo las preguntas tipo 'matrix' pueden tener subpreguntas."})

        # Validar unicidad de custom_identifier dentro de las subpreguntas de la misma pregunta padre
        if custom_identifier:
            siblings = SubQuestion.objects.filter(
                parent_question_id=parent_question_id)
            if siblings.filter(custom_identifier=custom_identifier).exists():
                raise DRFValidationError(
                    {"error": f"El identificador '{custom_identifier}' ya está en uso dentro de esta pregunta."})

        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Actualiza una subpregunta existente.")
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data
        custom_identifier = data.get('custom_identifier')

        # Validar unicidad de custom_identifier dentro de las subpreguntas de la misma pregunta padre
        if custom_identifier:
            siblings = SubQuestion.objects.filter(
                parent_question=instance.parent_question).exclude(id=instance.id)
            if siblings.filter(custom_identifier=custom_identifier).exists():
                return DRFResponse(
                    {"error": f"El identificador '{custom_identifier}' ya está en uso dentro de esta pregunta."},
                    status=400
                )

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Elimina una subpregunta específica.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class QuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD para preguntas (questions) asociadas a encuestas.
    """
    queryset = Question.objects.prefetch_related('subquestions', 'options')
    serializer_class = QuestionSerializer

    @swagger_auto_schema(operation_description="Lista de todas las preguntas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea una nueva pregunta.")
    def create(self, request, *args, **kwargs):
        data = request.data
        survey_id = data.get('survey')
        chapter_id = data.get('chapter')

        # Validar que se proporcione una encuesta o capítulo
        if not survey_id and not chapter_id:
            raise DRFValidationError(
                {"error": "Debe especificar una encuesta (survey) o un capítulo (chapter)."})

        # Validar que el capítulo pertenece a la encuesta
        if chapter_id and survey_id:
            chapter = Chapter.objects.filter(
                id=chapter_id, survey_id=survey_id).first()
            if not chapter:
                raise DRFValidationError(
                    {"error": "El capítulo no pertenece a la encuesta especificada."})

        # Crear la pregunta
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Pregunta creada con éxito.",
            "data": response.data
        }, status=201)

    @swagger_auto_schema(operation_description="Obtiene listado de preguntas y subpreguntas")
    def retrieve(self, request, *args, **kwargs):
        question = self.get_object()
        serializer = self.get_serializer(question)
        return Response(serializer.data)

    @swagger_auto_schema(operation_description="Actualiza una pregunta existente.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Elimina una pregunta específica.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["get", "post", "put", "delete"], url_path="subquestions")
    def subquestions(self, request, pk=None):
        """
        CRUD para subquestions de una pregunta específica.
        """
        question = self.get_object()

        if request.method == "GET":
            # Listar subpreguntas de esta pregunta
            subquestions = SubQuestion.objects.filter(parent_question=question)
            serializer = SubQuestionSerializer(subquestions, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            # Crear una subpregunta para esta pregunta
            data = request.data
            data["parent_question"] = question.id
            serializer = SubQuestionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)

        elif request.method == "PUT":
            # Actualizar una subpregunta específica
            subquestion_id = request.data.get("id")
            subquestion = SubQuestion.objects.get(
                id=subquestion_id, parent_question=question)
            serializer = SubQuestionSerializer(
                subquestion, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=200)

        elif request.method == "DELETE":
            # Eliminar una subpregunta específica
            subquestion_id = request.data.get("id")
            subquestion = SubQuestion.objects.get(
                id=subquestion_id, parent_question=question)
            subquestion.delete()
            return Response({"message": "Subquestion eliminada correctamente"}, status=204)


class OptionViewSet(viewsets.ModelViewSet):
    """
    CRUD para opciones (options) de preguntas y subpreguntas.
    """
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

    @swagger_auto_schema(operation_description="Lista de todas las opciones.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea una nueva opción.")
    def create(self, request, *args, **kwargs):
        """
        Validación para permitir opciones asociadas a preguntas y subpreguntas.
        """
        data = request.data
        if not data.get('question') and not data.get('subquestion'):
            raise DRFValidationError(
                {"error": "Debe asociar la opción a una pregunta o subpregunta."})
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Obtiene una opción específica por su ID.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Actualiza una opción existente.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Elimina una opción específica.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class SubmitResponseView(APIView):
    """
    Endpoint para registrar respuestas de usuarios a preguntas o subpreguntas, 
    validando primero si cumplen con los requisitos mínimos.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Registrar una o varias respuestas a preguntas o subpreguntas.",
        request_body=ResponseSerializer(many=True),
        responses={
            201: openapi.Response(description="Respuestas guardadas correctamente."),
            400: openapi.Response(description="Error en los datos enviados.")
        }
    )
    def post(self, request):
        user = request.user
        data = request.data

        # Verificar si data es una lista válida
        if not isinstance(data, list):
            return Response({"error": "El cuerpo de la solicitud debe ser una lista de respuestas."}, status=400)

        # Validar que cada elemento de `data` contenga `question_id`
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                return Response({"error": f"Cada respuesta debe ser un objeto JSON. Error en índice {idx}."}, status=400)
            if "question_id" not in item:
                return Response({"error": f"Cada respuesta debe contener 'question_id'. Faltante en índice {idx}."}, status=400)

        # Crear diccionario para acceso rápido a respuestas
        responses_dict = {item["question_id"]: item for item in data if "question_id" in item}

        # Validar pregunta clave: ¿Ha vivido en Colombia los últimos 5 años?
        response_colombia = responses_dict.get(1)
        if not response_colombia:
            return Response({"error": "Debe responder si ha vivido en Colombia los últimos 5 años."}, status=400)

        option_id = response_colombia.get("option_selected")
        if not option_id:
            return Response({"error": "Debe seleccionar una opción válida."}, status=400)

        option = get_object_or_404(Option, id=option_id)

        survey_id = response_colombia.get("survey_id")
        if not survey_id:
            return Response({"error": "Falta el ID de la encuesta (survey_id)."}, status=400)

        if option.text_option.lower() == "no":
            SurveyAttempt.objects.create(
                user=user,
                survey_id=survey_id,
                has_lived_in_colombia=False,
                rejection_note="El usuario no ha vivido en Colombia los últimos 5 años."
            )
            return Response({
                "message": "No cumple con los requisitos para la encuesta.",
                "rejected": True
            }, status=200)

        # Validar fecha de nacimiento si responde "Sí"
        response_birth_date = responses_dict.get(2)
        if not response_birth_date:
            return Response({"message": "Debe responder la fecha de nacimiento."}, status=206)

        try:
            birth_date = datetime.strptime(response_birth_date["answer"], "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Debe ser YYYY-MM-DD."}, status=400)

        today = date.today()
        if birth_date > today:
            return Response({"error": "Fecha futura inválida, seleccione una fecha de nacimiento correcta."}, status=400)

        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        if age < 18:
            SurveyAttempt.objects.create(
                user=user,
                survey_id=survey_id,
                has_lived_in_colombia=True,
                birth_date=birth_date,
                rejection_note=f"El usuario tiene {age} años y no cumple con la edad mínima."
            )
            return Response({
                "message": "No cumple con los requisitos de edad.",
                "rejected": True
            }, status=200)

        survey_attempt = SurveyAttempt.objects.create(
            user=user,
            survey_id=survey_id,
            has_lived_in_colombia=True,
            birth_date=birth_date,
            success_note="Encuesta diligenciada con éxito"
        )

        # Procesar respuestas restantes
        responses_data = [item for item in data if "question_id" in item and item["question_id"] not in [1, 2]]

        # Obtener todas las preguntas y opciones para optimizar consultas
        questions = {q.id: q for q in Question.objects.all()}
        options = {o.id: o for o in Option.objects.all()}

        # Validar que cada respuesta es un diccionario y contiene 'question_id'
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                return Response({"error": f"Cada respuesta debe ser un objeto JSON. Error en índice {idx}."}, status=400)
            if "question_id" not in item:
                return Response({"error": f"Cada respuesta debe contener 'question_id'. Faltante en índice {idx}."}, status=400)

        # Filtrar respuestas asegurando que 'question_id' está presente antes de acceder a él
        responses_data = [item for item in data if item.get("question_id") and item["question_id"] not in [1, 2]]

        for response_data in responses_data:
            subquestion_id = response_data.get("subquestion_id", None)

            if subquestion_id and isinstance(subquestion_id, SubQuestion):
                response_data["subquestion_id"] = subquestion_id.id

            if not isinstance(response_data, dict):
                return Response({"error": "Una de las respuestas no es un objeto JSON válido."}, status=400)

            question_id = response_data.get("question_id")


            if question_id is None:
                return Response({"error": "Una de las respuestas no tiene 'question_id'."}, status=400)

            # Manejo de opciones `is_other`
            option_selected_id = response_data.get("option_selected")
            other_text = response_data.get("other_text", "").strip()

            if option_selected_id:
                option = options.get(option_selected_id)

                if not option:
                    return Response({"error": f"La opción con ID {option_selected_id} no existe."}, status=400)

                if option.is_other and not other_text:
                    response_data["other_text"] = "Opción Otro sin responder"
                elif not option.is_other:
                    response_data.pop("other_text", None)

            # Manejo de subpreguntas `is_other`
            subquestion_id = response_data.get("subquestion_id")
            if subquestion_id:
                subquestion = get_object_or_404(SubQuestion, id=subquestion_id)
                if subquestion.is_other and not other_text:
                    response_data["other_text"] = "Opción Otro sin responder"
                elif not subquestion.is_other:
                    response_data.pop("other_text", None)

            # Validación de preguntas tipo matriz
            question = questions.get(question_id)
            if not question:
                return Response({"error": f"Pregunta con ID {question_id} no encontrada."}, status=400)

            if question.question_type == "matrix" and not subquestion_id:


                response_instance = {
                    "user": user.id,
                    "survey_attempt": survey_attempt.id,
                    "question": question_id,
                    "subquestion": subquestion_id,
                    "option_selected": option_selected_id,
                    "other_text": other_text if option and option.is_other else None
                }
                responses_data.append(response_instance)

        # Guardar respuestas
        # Debug descomentar esto al finalizar
        # serializer = ResponseSerializer(data=responses_data, many=True, context={'request': request})
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response({"message": "Respuestas guardadas exitosamente."}, status=201)

        # return Response(serializer.errors, status=400)
        
        # Debug - eliminar este código al finalizar el debug

        print("📦 Datos recibidos para guardar respuestas:") #Debug
        for item in responses_data:
            print(item)
        
        # try:
        #     serializer = ResponseSerializer(data=responses_data, many=True, context={'request': request})
        #     serializer.is_valid(raise_exception=True)
        #     serializer.save()
        #     return Response({"message": "Respuestas guardadas exitosamente."}, status=201)
        # except DRFValidationError as e:
        #     print("❌ Error de validación en ResponseSerializer:")
        #     print(e.detail)
        #     return Response({"error": str(e.detail)}, status=400)
        
        try:
            for item in responses_data:
                item["survey_attempt"] = survey_attempt.id

            serializer = ResponseSerializer(data=responses_data, many=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "Respuestas guardadas exitosamente."}, status=201)
        except DRFValidationError as e:
            print("❌ Error de validación en ResponseSerializer:")  # Debug
            print(e.detail) # Debug
            return Response({"error": str(e.detail)}, status=400)


class ResponseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint para registrar respuestas de usuarios a preguntas o subpreguntas,
    validando primero si cumplen con los requisitos mínimos.
    """
    queryset = ModelResponse.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(operation_description="Lista todas las respuestas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='export/(?P<format>[^/.]+)')
    def export(self, request, format=None):
        """
        Exportar respuestas en CSV, XLS o PDF con formato de fecha YYYY/MM/DD.
        """
        responses = self.queryset.select_related('user', 'question')
        data = tablib.Dataset()
        data.headers = ['ID', 'Usuario', 'Pregunta', 'Respuesta', 'Fecha']

        for response in responses:
            # Formato YYYY/MM/DD
            formatted_date = response.created_at.strftime('%Y/%m/%d %H:%M:%S')
            data.append([
                response.id,
                response.user.username,
                response.question.text_question,
                response.response_text or response.response_number,
                formatted_date,
            ])

        # Exportación en diferentes formatos
        if format == 'csv':
            response = HttpResponse(data.export('csv'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="responses.csv"'
        elif format == 'xls':
            response = HttpResponse(data.export('xls'), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="responses.xls"'
        elif format == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="responses.pdf"'
            doc = SimpleDocTemplate(response)
            table_data = [data.headers]  # Incluir encabezados
            for row in data.dict:
                table_data.append([
                    row['ID'], row['Usuario'], row['Pregunta'], row['Respuesta'], row['Fecha']
                ])
            table = Table(table_data)
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            table.setStyle(style)
            elements = [table]
            doc.build(elements)
        else:
            return DRFResponse({"error": "Formato no soportado."}, status=400)

        return response

    def post(self, request):
        """
        1. Verifica la pregunta: "¿Ha vivido en Colombia durante los últimos 5 años?"
        2. Si responde "No", se guarda un intento en `SurveyAttempt` y se rechaza la encuesta.
        3. Si responde "Sí", se valida la fecha de nacimiento.
        4. Si es menor de edad, se guarda un intento en `SurveyAttempt` y se rechaza la encuesta.
        5. Si es mayor de edad, se guardan todas las respuestas en `Response`.
        """
        user = request.user
        data = request.data
        responses_data = []

        question_live_in_colombia = get_object_or_404(
            Question, text_question="¿Ha vivido en Colombia durante los últimos 5 años?"
        )
        question_date_of_birth = get_object_or_404(
            Question, text_question="¿Cuál es su fecha de nacimiento?"
        )

        responses_dict = {item["question_id"]: item for item in data}

        # Extraer respuestas clave
        live_in_colombia_response = responses_dict.get(question_live_in_colombia.id)
        date_of_birth_response = responses_dict.get(question_date_of_birth.id)

        # Validar si respondió la residencia en Colombia
        if not live_in_colombia_response:
            return DRFResponse(
                {"error": "Debe responder si ha vivido en Colombia los últimos 5 años."},
                status=status.HTTP_400_BAD_REQUEST
            )

        option_id = live_in_colombia_response.get("option_selected")
        if not option_id:
            return DRFResponse(
                {"error": "Debe seleccionar una opción válida."},
                status=status.HTTP_400_BAD_REQUEST
            )

        live_in_colombia_opcion = get_object_or_404(Option, id=option_id)

        survey_id = live_in_colombia_response.get("survey_id")
        if not survey_id or not Survey.objects.filter(id=survey_id).exists():
            return DRFResponse({"error": "Encuesta inválida o no existente."}, status=status.HTTP_400_BAD_REQUEST)

        # Caso 1: Si responde "No" → Se rechaza la encuesta
        if live_in_colombia_opcion.text_option.lower() == "no":
            SurveyAttempt.objects.create(
                user=user,
                survey_id=survey_id,
                has_lived_in_colombia=False,
                rejection_note="El usuario no ha vivido en Colombia los últimos 5 años."
            )
            return DRFResponse({"message": "No cumple con los requisitos para la encuesta."}, status=status.HTTP_403_FORBIDDEN)

        # Caso 2: Si responde "Sí" pero no proporciona fecha de nacimiento
        if not date_of_birth_response or not date_of_birth_response.get("answer"):
            return DRFResponse(
                {"error": "Debe ingresar su fecha de nacimiento en formato YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Formato corregido a YYYY-MM-DD
            birth_date = datetime.strptime(date_of_birth_response["answer"], "%Y-%m-%d").date()
            age = relativedelta(now(), birth_date).years

            if age < 18:
                SurveyAttempt.objects.create(
                    user=user,
                    survey_id=survey_id,
                    has_lived_in_colombia=True,
                    birth_date=birth_date,
                    rejection_note=f"El usuario tiene {age} años y no cumple con el requisito de edad mínima."
                )
                return DRFResponse({"message": "No cumple con la edad mínima."}, status=status.HTTP_403_FORBIDDEN)

        except ValueError:
            return DRFResponse({"error": "Formato de fecha inválido. Debe ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Caso 3: Si cumple con los requisitos → Crear intento de encuesta
        survey_attempt = SurveyAttempt.objects.create(
            user=user,
            survey_id=survey_id,
            has_lived_in_colombia=True,
            birth_date=birth_date
        )

        # Guardar respuestas restantes
        responses_data = [item for item in data if item["question_id"] not in [question_live_in_colombia.id, question_date_of_birth.id]]

        serializer = ResponseSerializer(data=responses_data, many=True, context={'request': request})
        if serializer.is_valid():
            serializer.save(survey_attempt=survey_attempt)
            return DRFResponse({"message": "Respuestas guardadas exitosamente."}, status=status.HTTP_201_CREATED)

        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SaveGeographicResponseView(APIView):
    """
    Endpoint para guardar respuestas geográficas.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        question_id = data.get("question_id")
        user = request.user

        # Validación de datos
        if not question_id:
            return Response({"error": "El campo 'question_id' es obligatorio."}, status=400)

        try:
            # Extraer datos de respuesta
            country_code = data.get("country_code")
            department_code = data.get("department_code")
            municipality_code = data.get("municipality_code")

            country = None
            department = None
            municipality = None

            if country_code:
                # Si el país es distinto de "COLOMBIA", solo se guarda el país
                country = get_object_or_404(Country, numeric_code=country_code)

            if country_code == "COLOMBIA" or department_code:
                # Obtener departamento y municipio solo si se ha seleccionado un departamento
                department = get_object_or_404(
                    Department, code=department_code)
                municipality = get_object_or_404(
                    Municipality, code=municipality_code)

            # Guardar la respuesta en la BD
            ModelResponse.objects.create(
                user=user,
                question_id=question_id,
                country=country,
                department_id=department.id,
                municipality_id=municipality.id,
            )

            return Response({"message": "Respuesta geográfica guardada con éxito."}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)


class SurveyTextViewSet(viewsets.ModelViewSet):
    """
    ViewSet para realizar operaciones CRUD sobre SurveyText.
    """
    queryset = SurveyText.objects.all()
    serializer_class = SurveyTextSerializer

    def create(self, request, *args, **kwargs):
        survey_id = request.data.get('survey')
        title = request.data.get('title')

        # Validar que la encuesta exista
        if not Survey.objects.filter(id=survey_id).exists():
            raise DRFValidationError(
                {"error": "La encuesta especificada no existe."})

        # Validar que el título sea único para la encuesta
        if SurveyText.objects.filter(survey_id=survey_id, title=title).exists():
            raise DRFValidationError(
                {"error": "Ya existe un texto con este título para la encuesta especificada."})

        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Texto de encuesta creado con éxito.",
            "data": response.data
        }, status=201)
