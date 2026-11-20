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


class PaymentTests(APITestCase):
    fixtures = ["users", "materials", "payments"]

    def ids(self, query=""):
        r = self.client.get(f"/users/payments/{query}")
        self.assertEqual(r.status_code, 200, r.content)
        return [payment["id"] for payment in r.json()]

    def test_model_fields(self):
        from django.db import models

        from users.models import Payment

        f = {field.name: field for field in Payment._meta.get_fields()}
        self.assertIs(f["user"].related_model, User)
        self.assertEqual(f["paid_course"].related_model._meta.label, "materials.Course")
        self.assertEqual(f["paid_lesson"].related_model._meta.label, "materials.Lesson")
        self.assertIsInstance(f["payment_date"], models.DateTimeField)
        self.assertIsInstance(f["amount"], models.DecimalField)
        self.assertEqual(set(dict(Payment.PaymentMethod.choices)), {"cash", "transfer"})

    def test_fixtures_loaded(self):
        from users.models import Payment

        self.assertEqual(Payment.objects.count(), 8)

    def test_ordering_by_date(self):
        asc = self.ids("?ordering=payment_date")
        desc = self.ids("?ordering=-payment_date")
        self.assertEqual(asc, [101, 102, 103, 104, 105, 106, 107, 108])
        self.assertEqual(desc, list(reversed(asc)))
        self.assertEqual(self.ids(), desc)  # по умолчанию — сначала новые

    def test_filter_by_course_and_lesson(self):
        self.assertEqual(sorted(self.ids("?paid_course=101")), [101, 102])
        self.assertEqual(sorted(self.ids("?paid_course=102")), [104, 108])
        self.assertEqual(self.ids("?paid_lesson=104"), [103])
        self.assertEqual(self.ids("?paid_lesson=102"), [105])
        self.assertEqual(self.ids("?paid_lesson=101"), [])

    def test_filter_by_payment_method(self):
        self.assertEqual(sorted(self.ids("?payment_method=cash")), [102, 105, 106, 107])
        self.assertEqual(sorted(self.ids("?payment_method=transfer")), [101, 103, 104, 108])
        r = self.client.get("/users/payments/?payment_method=card")
        self.assertEqual(r.status_code, 400)

    def test_filters_combined(self):
        self.assertEqual(self.ids("?payment_method=cash&ordering=payment_date"), [102, 105, 106, 107])
        self.assertEqual(self.ids("?paid_course=102&payment_method=transfer"), [108, 104])

    def test_profile_payment_history(self):
        data = self.client.get("/users/101/").json()
        history = data["payments"]
        self.assertEqual([p["id"] for p in history], [107, 103, 101])
        lesson_payment = history[0]
        self.assertIsNone(lesson_payment["paid_course"])
        self.assertEqual(lesson_payment["paid_lesson"], {"id": 105, "title": "ViewSet и роутеры", "course": 102})
        self.assertEqual(lesson_payment["payment_method_display"], "Наличные")
        self.assertEqual(history[2]["paid_course"], {"id": 101, "title": "Python для начинающих"})

    def test_course_and_lesson_in_one_payment_forbidden(self):
        from django.db import IntegrityError, transaction

        from materials.models import Course, Lesson
        from users.models import Payment
        from users.serializers import PaymentSerializer

        serializer = PaymentSerializer(data={"user": 101, "paid_course": 101, "paid_lesson": 101,
                                             "amount": "100.00", "payment_method": "cash"})
        self.assertFalse(serializer.is_valid())
        with self.assertRaises(IntegrityError), transaction.atomic():
            Payment.objects.create(user_id=101, paid_course=Course.objects.get(pk=101),
                                   paid_lesson=Lesson.objects.get(pk=101), amount=1, payment_method="cash")
