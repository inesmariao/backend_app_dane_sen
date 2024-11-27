from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from .models import Survey, Question, Option
from .serializers import UserSerializer, SurveySerializer, QuestionSerializer, OptionSerializer

class WelcomeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Bienvenido/a a AppDiversa"})

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generar tokens para el usuario registrado
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "email": user.email,
                "name": user.name,
                "last_name": user.last_name
            },
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        })

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user is None:
            raise AuthenticationFailed("Email y/o contraseña inválidos")

        # Generar tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Agrega campos personalizados al token
        token['email'] = user.email
        token['name'] = user.name
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer
