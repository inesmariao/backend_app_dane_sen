from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    """
    Manager personalizado para el modelo CustomUser.

    Proporciona métodos para crear usuarios estándar y superusuarios.
    """
    def create_user(self, identifier=None, password=None, **extra_fields):
        """
        Crea un usuario estándar.

        Args:
            identifier (str): Puede ser un email, un username o un número de celular.
            password (str): Contraseña del usuario.
            **extra_fields: Campos adicionales para el usuario.

        Raises:
            ValueError: Si no se proporciona un identificador válido.

        Returns:
            CustomUser: Instancia del usuario creado.
        """
        if not identifier:
            raise ValueError("Debe proporcionar un email, username o número de celular para registrar al usuario.")

        if "@" in identifier:
            extra_fields['email'] = self.normalize_email(identifier)
        elif identifier.isdigit():
            extra_fields['phone_number'] = identifier
        else:
            extra_fields['username'] = identifier

        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, username=None, phone_number=None, password=None, **extra_fields):
        """
        Crea un superusuario con privilegios administrativos.

        Args:
            email (str): Dirección de correo electrónico.
            username (str): Nombre de usuario.
            phone_number (str): Número de celular.
            password (str): Contraseña del superusuario.
            **extra_fields: Campos adicionales.

        Returns:
            CustomUser: Instancia del superusuario creado.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not email:
            raise ValueError("Los superusuarios deben tener un email.")

        return self.create_user(email=email, username=username, phone_number=phone_number, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado.

    Este modelo permite registrar usuarios utilizando un email, un nombre de usuario (username)
    o un número de celular como identificador único.
    """
    email = models.EmailField(
        unique=True, blank=True, null=True,
        help_text="Dirección de correo electrónico única para cada usuario. Puede dejarse en blanco si se utiliza otro identificador."
    )
    username = models.CharField(
        max_length=30, unique=True, blank=True, null=True,
        help_text="Nombre de usuario único. Puede contener letras y números, sin espacios."
    )
    phone_number = models.CharField(
        max_length=15, unique=True, blank=True, null=True,
        validators=[RegexValidator(r'^\d+$', 'El número de celular solo debe contener dígitos.')],
        help_text="Número de celular único del usuario, solo se permiten dígitos."
    )
    name = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="Nombre del usuario."
    )
    last_name = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="Apellido del usuario."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica si la cuenta está activa."
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Indica si el usuario tiene acceso al panel de administración."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora en la que se creó el usuario."
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        """
        Representación en texto del modelo.

        Returns:
            str: Retorna el email, el username o el número de celular como representación.
        """
        if self.email:
            return self.email
        if self.username:
            return self.username
        return str(self.phone_number)
