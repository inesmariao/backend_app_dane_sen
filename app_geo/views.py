from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from .models import Country, Department, Municipality
from .serializers import CountrySerializer, DepartmentSerializer, MunicipalitySerializer, FileUploadSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import json
from django.http import JsonResponse


def get_departments(request):
    """
    Devuelve una lista de departamentos.
    """
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_municipalities(request, department_id):
    """
    Devuelve una lista de municipios según el id del departamento.
    """
    try:
        department = Department.objects.filter(id=department_id).first()
        if not department:
            return Response(
                {"error": "El departamento con el id proporcionado no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        municipalities = Municipality.objects.filter(department_code=department.code)

        if not municipalities.exists():
            return Response(
                {"message": "No se encontraron municipios para este departamento."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serializa y retorna los municipios
        serializer = MunicipalitySerializer(municipalities, many=True)

        return Response({"municipalities": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {"error": f"Ocurrió un error inesperado: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class CountryViewSet(ModelViewSet):
    """
    API para gestionar países.
    """
    permission_classes = [AllowAny]
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    @swagger_auto_schema(operation_summary="Listar todos los países.")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Crear un nuevo país.")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class DepartmentViewSet(ModelViewSet):
    """
    API para gestionar departamentos.
    """
    permission_classes = [AllowAny]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class MunicipalityViewSet(ModelViewSet):
    """
    API para gestionar municipios.
    """
    permission_classes = [AllowAny]
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer

    def get_queryset(self):
        department_code = self.request.query_params.get('department_code')
        if department_code:
            return Municipality.objects.filter(department__code=department_code)
        return Municipality.objects.all()

    serializer_class = MunicipalitySerializer

class FileUploadView(APIView):
    """
    API para cargar datos de países, departamentos y municipios desde archivos JSON o CSV.
    """
    @swagger_auto_schema(
        operation_summary="Subir archivo",
        operation_description="Permite subir un archivo JSON o CSV para crear/actualizar países, departamentos y municipios.",
        request_body=FileUploadSerializer,
        responses={200: openapi.Response("Éxito"), 400: "Error de formato"}
    )
    def post(self, request):
        file = request.FILES.get('file', None)
        if not file:
            raise ValidationError("No se proporcionó un archivo.")
        
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in ['json', 'csv']:
            raise ValidationError("Solo se permiten archivos JSON o CSV.")
        
        try:
            if file_extension == 'json':
                data = json.load(file)
                self._process_json(data)
            elif file_extension == 'csv':
                data = self._parse_csv(file)
                self._process_csv(data)
        except Exception as e:
            raise ValidationError(f"Error al procesar el archivo: {e}")
        
        return Response({"detail": "Datos cargados exitosamente."}, status=status.HTTP_200_OK)

    def _process_json(self, data):
        # Procesar datos del JSON
        from .models import Country, Department, Municipality
        for item in data:
            country_data = item.get('country', {})
            if country_data:
                country, _ = Country.objects.get_or_create(
                    alpha_2=country_data.get('alpha_2'),
                    defaults={
                        'spanish_name': country_data.get('spanish_name'),
                        'english_name': country_data.get('english_name'),
                        'alpha_3': country_data.get('alpha_3'),
                        'numeric_code': country_data.get('numeric_code')
                    }
                )

            for department_data in item.get('departments', []):
                department, _ = Department.objects.get_or_create(
                    code=department_data.get('code'),
                    defaults={
                        'name': department_data.get('name'),
                        'country': country
                    }
                )

                for municipality_data in department_data.get('municipalities', []):
                    Municipality.objects.get_or_create(
                        code=municipality_data.get('code'),
                        defaults={
                            'name': municipality_data.get('name'),
                            'department': department
                        }
                    )

    def _parse_csv(self, file):
        # Parsear el archivo CSV
        import csv
        reader = csv.DictReader(file.read().decode('utf-8').splitlines())
        return list(reader)

    def _process_csv(self, file):
        # Procesar datos del CSV
        import csv
        from .models import Country, Department, Municipality

        reader = csv.DictReader(file.read().decode('utf-8').splitlines())
        for row in reader:
            try:
                country, _ = Country.objects.get_or_create(
                    alpha_2=row.get('country_alpha_2'),
                    defaults={
                        'spanish_name': row.get('country_spanish_name'),
                        'english_name': row.get('country_english_name'),
                        'alpha_3': row.get('country_alpha_3'),
                        'numeric_code': row.get('country_numeric_code')
                    }
                )
                department, _ = Department.objects.get_or_create(
                    code=row.get('department_code'),
                    defaults={
                        'name': row.get('department_name'),
                        'country': country
                    }
                )
                Municipality.objects.get_or_create(
                    code=row.get('municipality_code'),
                    defaults={
                        'name': row.get('municipality_name'),
                        'department': department
                    }
                )
            except Exception as e:
                raise ValidationError(f"Error al procesar el archivo CSV: {e}")
