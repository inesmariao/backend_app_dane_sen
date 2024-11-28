from rest_framework import serializers
from ..models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """
        Serializer para manejar la creación y validación de usuarios.
        Permite registrar un usuario utilizando email, username o número de teléfono como identificador.
        Utiliza los `help_text` definidos en el modelo `CustomUser`.
    """
    identifier = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Identificador único del usuario. Puede ser un email, un nombre de usuario o un número de celular."
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Contraseña para la cuenta del usuario."
    )


    class Meta:
        model = CustomUser
        fields = ['identifier', 'password', 'name', 'last_name']
        extra_kwargs = {
            'name': {'required': False, 'help_text': "Nombre del usuario (opcional)."},
            'last_name': {'required': False, 'help_text': "Apellido del usuario (opcional)."}
        }

    def validate_identifier(self, value):
        """
        Verifica que el identifier (email, username o phone_number) no esté ya registrado.

        - Si el identificador es un email, se valida que no exista en la base de datos.
        - Si es un número de celular, se verifica su unicidad.
        - Si es un username, también se comprueba que no esté ya en uso.

        Args:
            value (str): Identificador proporcionado por el usuario.

        Returns:
            str: El valor validado si pasa las verificaciones.

        Raises:
            serializers.ValidationError: Si el identificador ya está registrado.
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
        """
        Crea un nuevo usuario basado en el identificador proporcionado.

        El identificador puede ser:
        - Un email: se almacena en el campo `email`.
        - Un número de celular: se almacena en el campo `phone_number`.
        - Un username: se almacena en el campo `username`.

        Args:
            validated_data (dict): Datos validados del usuario.

        Returns:
            CustomUser: El usuario creado.
        """
        identifier = validated_data.pop('identifier')
        password = validated_data.pop('password')

        if '@' in identifier:  # Caso: Email
            validated_data['email'] = identifier
        elif identifier.isdigit():  # Caso: Número de celular
            validated_data['phone_number'] = identifier
        else:  # Caso: Username
            validated_data['username'] = identifier

        return CustomUser.objects.create_user(identifier=identifier, password=password, **validated_data)