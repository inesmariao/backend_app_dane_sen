from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response as DRFResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer
from ..models import CustomUser
from django.db.models import Q

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

        return DRFResponse({
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
                        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "user": {
                            "id": 1,
                            "username": "example_user",
                            "email": "example@example.com",
                            "phone_number": "1234567890"
                        }
                    }
                }
            ),
            400: "Identificador o contraseña incorrectos."
        }
    )

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        user = CustomUser.objects.filter(
            Q(email=identifier) | Q(phone_number=identifier) | Q(username=identifier),
            is_deleted=False
        ).first()

        # Verificar contraseña para todos los casos
        if user and not user.check_password(password):
            user = None

        if not user:
            return DRFResponse({"error": "Identificador o contraseña incorrectos."}, status=400)

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)

        return DRFResponse({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
            }
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

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD para usuarios.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Lista todos los usuarios.
        """
        # Excluir eliminados
        queryset = self.queryset.filter(is_deleted=False)
        serializer = self.serializer_class(queryset, many=True)
        return DRFResponse(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        Obtiene un usuario específico por su ID.
        """
        try:
            user = self.queryset.filter(is_deleted=False).get(pk=pk)
            serializer = self.serializer_class(user)
            return DRFResponse(serializer.data)
        except CustomUser.DoesNotExist:
            return DRFResponse({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo usuario.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return DRFResponse(serializer.data, status=status.HTTP_201_CREATED)
        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        """
        Actualiza un usuario existente.
        """
        try:
            user = self.queryset.get(pk=pk)
            serializer = self.serializer_class(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return DRFResponse(serializer.data)
            return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return DRFResponse({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None, *args, **kwargs):
        """
        Elimina un usuario de manera lógica.
        """
        try:
            user = self.queryset.get(pk=pk)
            user.delete()  # Usa el método sobrescrito para eliminar lógicamente
            return DRFResponse({"message": "Usuario eliminado exitosamente."}, status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return DRFResponse({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)