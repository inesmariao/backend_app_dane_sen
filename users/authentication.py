from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

CustomUser = get_user_model()

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autenticar usando email, username o número de celular.
        """
        try:
            user = CustomUser.objects.get(
                Q(email=username) |  # Consulta para email
                Q(username=username) |  # Consulta para username
                Q(phone_number=username)  # Consulta para número de celular
            )
        except CustomUser.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
