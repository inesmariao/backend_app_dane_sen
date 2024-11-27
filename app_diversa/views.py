from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from .models import Survey, Question, Option
from .serializers import UserSerializer, SurveySerializer, QuestionSerializer, OptionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def welcome_view(request):
    return Response({"message": "Bienvenido/a a AppDiversa"})

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=201)
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        return Response({"error": "Credenciales inválidas"}, status=400)

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
