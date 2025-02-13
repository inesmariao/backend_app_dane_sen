from rest_framework import serializers
from .models import Country, Department, Municipality

class CountrySerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo `Country`.
    """
    class Meta:
        model = Country
        fields = ['id', 'spanish_name', 'english_name', 'alpha_3', 'alpha_2', 'numeric_code']


class MunicipalitySerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo `Municipality`.
    """
    department_code = serializers.IntegerField()

    class Meta:
        model = Municipality
        fields = ['id', 'code', 'name', 'department_code']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo `Department`.

    Incluye la lista de municipios pertenecientes al departamento.
    """
    municipalities = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'municipalities']

    def get_municipalities(self, obj):
        """
        Devuelve una lista de municipios relacionados con este departamento.
        """
        return list(Municipality.objects.filter(department_code=obj.code).values('code', 'name'))


class FileUploadSerializer(serializers.Serializer):
    """
    Serializador para la carga de archivos (JSON o CSV).
    """
    file = serializers.FileField()
