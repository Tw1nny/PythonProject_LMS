from django.contrib.auth.models import AbstractBaseUser
from rest_framework.test import APITestCase

from users.models import User


class UserModelTests(APITestCase):
    def test_model(self):
        self.assertTrue(issubclass(User, AbstractBaseUser))
        self.assertEqual(User.USERNAME_FIELD, "email")
        fields = {f.name for f in User._meta.get_fields()}
        self.assertTrue({"phone", "city", "avatar", "first_name", "last_name", "is_active"} <= fields)
        self.assertNotIn("username", fields)
        user = User.objects.create_user("Student@Example.com", "Str0ng-Pass-2026")
        self.assertEqual(user.email, "student@example.com")
        self.assertTrue(self.client.login(email="student@example.com", password="Str0ng-Pass-2026"))


class UserProfileAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("student@example.com", "Str0ng-Pass-2026")

    def test_list_and_retrieve(self):
        self.assertEqual(self.client.get("/users/").status_code, 200)
        r = self.client.get(f"/users/{self.user.pk}/")
        self.assertEqual(r.json()["email"], "student@example.com")
        self.assertNotIn("password", r.json())

    def test_update_profile(self):
        r = self.client.patch(f"/users/{self.user.pk}/", {"phone": "+7 999 123-45-67", "city": "Москва"})
        self.assertEqual(r.status_code, 200, r.json())
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, "Москва")

    def test_cannot_change_password_or_rights(self):
        old_hash = self.user.password
        self.client.patch(f"/users/{self.user.pk}/", {"password": "x", "is_superuser": True})
        self.user.refresh_from_db()
        self.assertEqual(self.user.password, old_hash)
        self.assertFalse(self.user.is_superuser)
