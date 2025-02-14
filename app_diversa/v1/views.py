from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Survey, Question, SubQuestion, Option, Chapter, SurveyText, Response as ModelResponse
from .serializers import SurveySerializer, QuestionSerializer, SubQuestionSerializer, OptionSerializer, ResponseSerializer, ChapterSerializer, SurveyTextSerializer
from app_geo.models import Country, Department, Municipality
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
import tablib
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from rest_framework.response import Response


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
        return DRFResponse(data)

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
        return DRFResponse(data)

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
                return DRFResponse({"error": "La pregunta padre no existe."}, status=400)
            if parent_question.question_type != "matrix":
                return DRFResponse({"error": "Solo las preguntas tipo 'matrix' pueden tener subpreguntas."}, status=400)

        # Validar unicidad de custom_identifier dentro de las subpreguntas de la misma pregunta padre
        if custom_identifier:
            siblings = SubQuestion.objects.filter(parent_question_id=parent_question_id)
            if siblings.filter(custom_identifier=custom_identifier).exists():
                return DRFResponse(
                    {"error": f"El identificador '{custom_identifier}' ya está en uso dentro de esta pregunta."},
                    status=400
                )

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

    @swagger_auto_schema(operation_description="Obtiene listado de preguntas y subpreguntas")
    def retrieve(self, request, *args, **kwargs):
        question = self.get_object()
        serializer = self.get_serializer(question)
        return DRFResponse(serializer.data)

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
            return DRFResponse({"error": "Debe asociar la opción a una pregunta o subpregunta."}, status=400)
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

        try:
            # Extraer datos de respuesta
            country_id = data.get("country_id")
            department_code = data.get("department_code")
            municipality_code = data.get("municipality_code")

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

    @action(detail=False, methods=['get'], url_path='export/(?P<format>[^/.]+)')
    def export(self, request, format=None):
        responses = self.queryset.select_related('user', 'question')
        data = tablib.Dataset()
        data.headers = ['ID', 'Usuario', 'Pregunta', 'Respuesta', 'Fecha']

        for response in responses:
            data.append([
                response.id,
                response.user.username,
                response.question.text,
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
            return DRFResponse({"error": "Formato no soportado."}, status=400)

        return response