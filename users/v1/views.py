from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from ..models import CustomUser

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "email": user.email,
                "username": user.username,
                "phone_number": user.phone_number,
            },
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        if "@" in identifier:  # Login con email
            user = CustomUser.objects.filter(email=identifier).first()
        elif identifier.isdigit():  # Login con número de teléfono
            user = CustomUser.objects.filter(phone_number=identifier).first()
        else:  # Login con username
            user = CustomUser.objects.filter(username=identifier).first()

        # Verifica contraseña para todos los casos
        if user and not user.check_password(password):
            user = None

        if not user:
            return Response({"error": "Identificador o contraseña incorrectos."}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Agregar datos personalizados al token
        token['email'] = user.email
        token['username'] = user.username
        token['phone_number'] = user.phone_number
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer