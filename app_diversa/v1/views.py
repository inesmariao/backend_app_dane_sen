from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models import Survey, Question, Option
from .serializers import SurveySerializer, QuestionSerializer, OptionSerializer, ResponseSerializer

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
            return Response({"message": "Respuesta enviada correctamente."})
        return Response(serializer.errors, status=400)