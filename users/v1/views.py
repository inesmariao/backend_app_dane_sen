from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer
from ..models import CustomUser

class RegisterView(APIView):
    """
    Registro de Usuarios.

    Permite registrar un nuevo usuario utilizando un identificador único
    (email, username o número de celular) y una contraseña.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Registrar un nuevo usuario utilizando email, username o número de teléfono.",
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                description="Usuario creado exitosamente.",
                examples={
                    "application/json": {
                        "user": {
                            "email": "example@example.com",
                            "username": "example_user",
                            "phone_number": "1234567890"
                        },
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                }
            ),
            400: "Solicitud inválida: error en la validación de datos."
        }
    )

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
    """
    Inicio de Sesión.

    Permite a los usuarios iniciar sesión utilizando su identificador único
    (email, username o número de celular) y contraseña.
    """
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Iniciar sesión utilizando email, username o número de teléfono.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "identifier": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Email, username o número de teléfono del usuario."
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Contraseña del usuario."
                ),
            },
            required=["identifier", "password"]
        ),
        responses={
            200: openapi.Response(
                description="Inicio de sesión exitoso.",
                examples={
                    "application/json": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                }
            ),
            400: "Identificador o contraseña incorrectos."
        }
    )

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