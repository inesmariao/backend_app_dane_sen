from django.test import TestCase
from users.models import CustomUser

class CustomUserTests(TestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(identifier="testuser", password="123456")
        self.assertTrue(user.username, "testuser")

    def test_delete_user(self):
        user = CustomUser.objects.create_user(identifier="testuser", password="123456")
        user.delete()
        self.assertTrue(user.is_deleted)
        self.assertFalse(user.is_active)
