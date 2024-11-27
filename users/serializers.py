from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    identifier = serializers.CharField(write_only=True, required=True)  # Puede ser email, username o phone_number
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['identifier', 'password', 'name', 'last_name']

    def validate_identifier(self, value):
        """
        Verifica si el identifier (email, username o phone_number) ya existe.
        """
        if '@' in value:  # Verifica email
            if CustomUser.objects.filter(email=value).exists():
                raise serializers.ValidationError("El email ya está registrado.")
        elif value.isdigit():  # Verifica número de celular
            if CustomUser.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("El número de celular ya está registrado.")
        else:  # Verifica username
            if CustomUser.objects.filter(username=value).exists():
                raise serializers.ValidationError("El nombre de usuario ya está registrado.")
        return value

    def create(self, validated_data):
        identifier = validated_data.pop('identifier')
        password = validated_data.pop('password')

        if '@' in identifier:  # Caso: Email
            validated_data['email'] = identifier
        elif identifier.isdigit():  # Caso: Número de celular
            validated_data['phone_number'] = identifier
        else:  # Caso: Username
            validated_data['username'] = identifier

        return CustomUser.objects.create_user(identifier=identifier, password=password, **validated_data)