from rest_framework import serializers
from .models import Country, Department, Municipality

class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ['id', 'code', 'name']

class DepartmentSerializer(serializers.ModelSerializer):
    municipalities = MunicipalitySerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'code', 'name', 'country', 'municipalities']

class CountrySerializer(serializers.ModelSerializer):
    departments = DepartmentSerializer(many=True, read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'spanish_name', 'english_name', 'alpha_3', 'alpha_2', 'numeric_code', 'departments']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
