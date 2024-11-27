from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, identifier=None, password=None, **extra_fields):
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
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not email:
            raise ValueError("Los superusuarios deben tener un email.")

        return self.create_user(email=email, username=username, phone_number=phone_number, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=True, null=True)
    username = models.CharField(max_length=30, unique=True, blank=True, null=True)
    phone_number = models.CharField(
        max_length=15, unique=True, blank=True, null=True,
        validators=[RegexValidator(r'^\d+$', 'El número de celular solo debe contener dígitos.')]
    )
    name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.email:
            return self.email
        if self.username:
            return self.username
        return str(self.phone_number)
