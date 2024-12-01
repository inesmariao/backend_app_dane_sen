from django.test import TestCase
from .models import CustomUser

class CustomUserTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password123")

    def test_logical_delete(self):
        self.user.delete()
        self.assertTrue(self.user.is_deleted)
        self.assertFalse(self.user.is_active)
        self.assertFalse(CustomUser.objects.filter(id=self.user.id).exists())
