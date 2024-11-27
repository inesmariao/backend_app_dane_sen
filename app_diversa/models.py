from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Module(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Survey(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Question(models.Model):
    QUESTION_TYPES = [
        ('open', 'Pregunta Abierta'),
        ('closed', 'Pregunta Cerrada'),
        ('likert', 'Escala Likert'),
        ('rating', 'Escala de Puntuación'),
        ('matrix', 'Pregunta Matricial'),
    ]

    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    is_required = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_other = models.BooleanField(default=False)  # Indica si es una opción "Otro".
    created_at = models.DateTimeField(auto_now_add=True)

