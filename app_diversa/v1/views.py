from datetime import datetime
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response as DRFResponse
from rest_framework.serializers import ValidationError as DRFValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import SurveyAttempt, Survey, Question, SubQuestion, Option, Chapter, SurveyText
from ..models import Response as ModelResponse
from .serializers import SurveyAttemptSerializer, SurveySerializer, QuestionSerializer, SubQuestionSerializer, OptionSerializer, ResponseSerializer, ChapterSerializer, SurveyTextSerializer
from app_geo.models import Country, Department, Municipality
import tablib
from reportlab.pdfgen import canvas


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
        questions = Question.objects.filter(survey=survey, parent_question__isnull=True).prefetch_related(
            'subquestions', 'options'
        )
        serializer = self.get_serializer(survey)
        data = serializer.data
        data['title'] = survey.title
        data['description_name'] = survey.description_name
        data['description_title'] = survey.description_title
        return Response(data)

    @swagger_auto_schema(operation_description="Actualiza una encuesta existente.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Elimina una encuesta específica.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        survey = self.get_object()
        serializer = self.get_serializer(survey)
        data = serializer.data
        data['questions'] = sorted(data['questions'], key=lambda q: q['order_question'])
        return Response(data)

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
            parent_question = Question.objects.filter(id=parent_question_id).first()
            if not parent_question:
                raise DRFValidationError({"error": "La pregunta padre no existe."})
            if parent_question.question_type != "matrix":
                raise DRFValidationError({"error": "Solo las preguntas tipo 'matrix' pueden tener subpreguntas."})

        # Validar unicidad de custom_identifier dentro de las subpreguntas de la misma pregunta padre
        if custom_identifier:
            siblings = SubQuestion.objects.filter(parent_question_id=parent_question_id)
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
            siblings = SubQuestion.objects.filter(parent_question=instance.parent_question).exclude(id=instance.id)
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
            raise DRFValidationError({"error": "Debe especificar una encuesta (survey) o un capítulo (chapter)."})

        # Validar que el capítulo pertenece a la encuesta
        if chapter_id and survey_id:
            chapter = Chapter.objects.filter(id=chapter_id, survey_id=survey_id).first()
            if not chapter:
                raise DRFValidationError({"error": "El capítulo no pertenece a la encuesta especificada."})

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
            subquestion = SubQuestion.objects.get(id=subquestion_id, parent_question=question)
            serializer = SubQuestionSerializer(subquestion, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=200)

        elif request.method == "DELETE":
            # Eliminar una subpregunta específica
            subquestion_id = request.data.get("id")
            subquestion = SubQuestion.objects.get(id=subquestion_id, parent_question=question)
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
            raise DRFValidationError({"error": "Debe asociar la opción a una pregunta o subpregunta."})
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
    Endpoint para registrar respuestas de usuarios a preguntas o subpreguntas, validando primero si cumplen con los requisitos mínimos.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Registrar una o varias respuestas a preguntas o subpreguntas.",
        request_body=ResponseSerializer(many=True),
        responses={201: openapi.Response(description="Respuestas guardadas correctamente."),
                    400: openapi.Response(description="Error en los datos enviados.")}
    )
    def post(self, request):
        """
        Validación antes de registrar respuestas:
        1. Verifica la pregunta: "¿Ha vivido en Colombia durante los últimos 5 años?"
        2. Si responde "No", se guarda un intento en `SurveyAttempt` y se rechaza la encuesta.
        3. Si responde "Sí", se valida la fecha de nacimiento.
        4. Si es menor de edad, se guarda un intento en `SurveyAttempt` y se rechaza la encuesta.
        5. Si es mayor de edad, se guardan todas las respuestas en `Response`.
        """
        user = request.user
        data = request.data
        responses_data = []
        
        import json  # Debug
        print(f"\n🔥 DEBUG - Request data recibida:\n{json.dumps(request.data, indent=4)}")  # Debug

        # Obtener las preguntas de validación
        question_live_in_colombia = get_object_or_404(Question, text_question="¿Ha vivido en Colombia durante los últimos 5 años?")
        question_date_of_birth = get_object_or_404(Question, text_question="¿Cuál es su fecha de nacimiento?")

        live_in_colombia_response = None
        date_of_birth_response = None

        # Extraer las respuestas de validación
        for item in data:
            if item["question_id"] == question_live_in_colombia.id:
                live_in_colombia_response = item
            elif item["question_id"] == question_date_of_birth.id:
                date_of_birth_response = item
            else:
                responses_data.append(item)  # Guardar otras respuestas temporalmente

        # Primera Validación: "¿Ha vivido en Colombia?"

        print(f"🔍 DEBUG - Respuesta a '¿Ha vivido en Colombia?': {live_in_colombia_response}")  # Debug

        if not live_in_colombia_response or live_in_colombia_response.get("option_selected") is None:
            return DRFResponse({"error": "Debe responder si ha vivido en Colombia los últimos 5 años."}, status=status.HTTP_400_BAD_REQUEST)

        live_in_colombia_opcion = get_object_or_404(Option, id=live_in_colombia_response["option_selected"])
        
        survey_id = request.data[0].get("survey_id", None)

        if live_in_colombia_opcion.text_option.lower() == "no":
            # Si responde "No", se guarda en `SurveyAttempt` y se rechaza la encuesta
            SurveyAttempt.objects.create(
                user=user,
                survey_id=survey_id,
                has_lived_in_colombia=False,
                rejection_note="El usuario no ha vivido en Colombia los últimos 5 años."
            )
            return DRFResponse({"message": "No cumple con los requisitos para la encuesta."}, status=status.HTTP_403_FORBIDDEN)

        # Segunda Validación: Fecha de nacimiento
        print(f"🔍 DEBUG - Respuesta a 'Fecha de nacimiento': {date_of_birth_response}")  # Debug

        if not date_of_birth_response or not date_of_birth_response.get("answer"):
            return DRFResponse({"error": "Debe ingresar su fecha de nacimiento."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            birth_date = datetime.strptime(date_of_birth_response["answer"], "%Y-%m-%d").date()
        except ValueError:
            return DRFResponse({"error": "Formato de fecha inválido. Debe ser YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        age = relativedelta(now(), birth_date).years

        if age < 18:
            # Si es menor de 18 años, se rechaza y se guarda en `SurveyAttempt`
            SurveyAttempt.objects.create(
                user=user,
                survey_id=survey_id,
                has_lived_in_colombia=True,
                birth_day=birth_date.day,
                birth_month=birth_date.month,
                birth_year=birth_date.year,
                rejection_note=f"El usuario tiene {age} años, no cumple con el requisito de edad mínima."
            )
            return DRFResponse({"message": "No cumple con los requisitos de age para la encuesta."}, status=status.HTTP_403_FORBIDDEN)

        # ✅ **Crear registro en `SurveyAttempt` si pasa las validaciones**
        survey_attempt = SurveyAttempt.objects.create(
            user=user,
            survey_id=survey_id,
            has_lived_in_colombia=True,
            birth_day=birth_date.day,
            birth_month=birth_date.month,
            birth_year=birth_date.year
        )

        # Si pasó ambas validaciones, se guardan todas las respuestas en `Response`
        serializer = ResponseSerializer(data=responses_data, many=True, context={'request': request})

        if serializer.is_valid():
            try:
                responses = serializer.save(survey_attempt=survey_attempt)

                return DRFResponse({"message": "Respuestas guardadas exitosamente"},
                                    status=status.HTTP_201_CREATED)

            except (ValueError, TypeError, DRFValidationError) as e:
                print(f"❌ Error de validación o tipo de dato: {e}") # Debug
                return DRFResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                print(f"❌ Error durante la creación de respuesta: {e}") # Debug
                return DRFResponse({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            print(f"❌ ERROR - Datos del request no válidos:\n{json.dumps(serializer.errors, indent=4)}") # Debug
            return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResponseViewSet(viewsets.ReadOnlyModelViewSet):  
    """
    ViewSet para ver respuestas asociadas a preguntas. **Solo lectura**.
    """
    queryset = ModelResponse.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Lista todas las respuestas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='export/(?P<format>[^/.]+)')
    def export(self, request, format=None):
        """
        Exportar respuestas en CSV, XLS o PDF.
        """
        responses = self.queryset.select_related('user', 'question')
        data = tablib.Dataset()
        data.headers = ['ID', 'Usuario', 'Pregunta', 'Respuesta', 'Fecha']

        for response in responses:
            data.append([
                response.id,
                response.user.username,
                response.question.text_question,
                response.response_text or response.response_number,
                response.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])

        if format == 'csv':
            response = HttpResponse(data.export('csv'), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="responses.csv"'
        elif format == 'xls':
            response = HttpResponse(data.export('xls'), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="responses.xls"'
        elif format == 'pdf':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="responses.pdf"'
            p = canvas.Canvas(response)
            y = 800
            for row in data.dict:
                p.drawString(100, y, f"{row['ID']} - {row['Usuario']} - {row['Pregunta']} - {row['Respuesta']} - {row['Fecha']}")
                y -= 20
            p.showPage()
            p.save()
        else:
            return Response({"error": "Formato no soportado."}, status=400)

        return response


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
            raise DRFValidationError({"error": "El campo 'question_id' es obligatorio."})

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
                department = get_object_or_404(Department, code=department_code)
                municipality = get_object_or_404(Municipality, code=municipality_code)

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
            raise DRFValidationError({"error": "La encuesta especificada no existe."})

        # Validar que el título sea único para la encuesta
        if SurveyText.objects.filter(survey_id=survey_id, title=title).exists():
            raise DRFValidationError({"error": "Ya existe un texto con este título para la encuesta especificada."})

        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Texto de encuesta creado con éxito.",
            "data": response.data
        }, status=201)
