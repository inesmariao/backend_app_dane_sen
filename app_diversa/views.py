from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Survey, Question, Option
from .serializers import SurveySerializer, QuestionSerializer, OptionSerializer, ResponseSerializer

class WelcomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Bienvenido/a a AppDiversa"})

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

class SubmitResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ResponseSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Respuesta enviada correctamente."})
        return Response(serializer.errors, status=400)