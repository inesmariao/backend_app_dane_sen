from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse  # Alias más descriptivo
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Survey, Question, Option, Chapter, SurveyText, Response as ModelResponse  # Alias descriptivo
from .serializers import SurveySerializer, QuestionSerializer, OptionSerializer, ResponseSerializer, ChapterSerializer, SurveyTextSerializer
from app_geo.models import Country, Department, Municipality
from django.shortcuts import get_object_or_404

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
        return DRFResponse({"message": "Bienvenido/a a AppDiversa"})

class SurveyViewSet(viewsets.ModelViewSet):
    """
    CRUD para encuestas (surveys).
    """
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

    @swagger_auto_schema(operation_description="Lista de todas las encuestas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea una nueva encuesta.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Obtiene una encuesta específica por su ID.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Actualiza una encuesta existente.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Elimina una encuesta específica.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class ChapterViewSet(viewsets.ModelViewSet):
    """
    ViewSet para realizar operaciones CRUD sobre Chapter.
    """
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    """
    CRUD para preguntas (questions) asociadas a encuestas.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    @swagger_auto_schema(operation_description="Lista de todas las preguntas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea una nueva pregunta.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Obtiene una pregunta específica por su ID.")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Actualiza una pregunta existente.")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Elimina una pregunta específica.")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        survey_id = data.get('survey')
        chapter_id = data.get('chapter')

        # Validar que se proporcione una encuesta o capítulo
        if not survey_id and not chapter_id:
            return DRFResponse({"error": "Debe especificar una encuesta (survey) o un capítulo (chapter)."}, status=400)

        # Validar que el capítulo pertenece a la encuesta
        if chapter_id and survey_id:
            chapter = Chapter.objects.filter(id=chapter_id, survey_id=survey_id).first()
            if not chapter:
                return DRFResponse({"error": "El capítulo no pertenece a la encuesta especificada."}, status=400)

        # Crear la pregunta
        response = super().create(request, *args, **kwargs)
        return DRFResponse({
            "message": "Pregunta creada con éxito.",
            "data": response.data
        }, status=201)

class OptionViewSet(viewsets.ModelViewSet):
    """
    CRUD para opciones (options) de preguntas.
    """
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

    @swagger_auto_schema(operation_description="Lista de todas las opciones.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea una nueva opción.")
    def create(self, request, *args, **kwargs):
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
    Endpoint para registrar respuestas de usuarios a preguntas.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Registrar una respuesta a una pregunta.",
        request_body=ResponseSerializer,
        responses={
            201: openapi.Response(description="Respuesta enviada correctamente."),
            400: openapi.Response(description="Datos de la respuesta inválidos.")
        }
    )

    def post(self, request):
        serializer = ResponseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return DRFResponse({"message": "Respuesta enviada correctamente."}, status=201)
        return DRFResponse(serializer.errors, status=400)

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
            return DRFResponse({"error": "El campo 'question_id' es obligatorio."}, status=400)

        # Extraer datos de respuesta
        country_id = data.get("country_id")
        department_code = data.get("department_code")
        municipality_code = data.get("municipality_code")

        try:
            if country_id == "COLOMBIA":
                # Si es Colombia, obtener departamento y municipio
                department = get_object_or_404(Department, code=department_code)
                municipality = get_object_or_404(Municipality, code=municipality_code)

                # Crear respuesta
                ModelResponse.objects.create(
                    user=user,
                    question_id=question_id,
                    country=None,
                    department=department,
                    municipality=municipality,
                )
            else:
                # Si es otro país, guardar solo el país
                country = get_object_or_404(Country, id=country_id)
                ModelResponse.objects.create(
                    user=user,
                    question_id=question_id,
                    country=country,
                    department=None,
                    municipality=None,
                )

            return DRFResponse({"message": "Respuesta guardada con éxito."}, status=201)

        except Exception as e:
            return DRFResponse({"error": str(e)}, status=400)

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
            return DRFResponse({"error": "La encuesta especificada no existe."}, status=400)

        # Validar que el título sea único para la encuesta
        if SurveyText.objects.filter(survey_id=survey_id, title=title).exists():
            return DRFResponse({"error": "Ya existe un texto con este título para la encuesta especificada."}, status=400)

        response = super().create(request, *args, **kwargs)
        return DRFResponse({
            "message": "Texto de encuesta creado con éxito.",
            "data": response.data
        }, status=201)

class ResponseViewSet(viewsets.ModelViewSet):
    """
    CRUD para respuestas asociadas a preguntas.
    """
    queryset = ModelResponse.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Lista todas las respuestas.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Crea una nueva respuesta.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)