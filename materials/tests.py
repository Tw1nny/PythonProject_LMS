import io
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson

TEMP_MEDIA = tempfile.mkdtemp()


def make_image(name="preview.png"):
    buffer = io.BytesIO()
    Image.new("RGB", (20, 20), "green").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class CourseAPITests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.course = Course.objects.create(title="Python", description="Основы")

    def test_list_and_retrieve(self):
        r = self.client.get("/courses/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json()[0]["title"], "Python")
        r = self.client.get(f"/courses/{self.course.pk}/")
        self.assertEqual(r.json()["description"], "Основы")

    def test_create_with_preview(self):
        r = self.client.post("/courses/", {"title": "Django", "description": "DRF", "preview": make_image()},
                             format="multipart")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.json())
        self.assertTrue(r.json()["preview"].endswith(".png"))
        self.assertEqual(Course.objects.count(), 2)

    def test_update(self):
        r = self.client.put(f"/courses/{self.course.pk}/", {"title": "Python 2", "description": "Новое"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        r = self.client.patch(f"/courses/{self.course.pk}/", {"title": "Python 3"})
        self.assertEqual(r.json()["title"], "Python 3")
        self.assertEqual(r.json()["description"], "Новое")

    def test_delete(self):
        r = self.client.delete(f"/courses/{self.course.pk}/")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.exists())

    def test_validation(self):
        r = self.client.post("/courses/", {"description": "без названия"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", r.json())


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class LessonAPITests(APITestCase):
    def setUp(self):
        self.course = Course.objects.create(title="Python")
        self.lesson = Lesson.objects.create(title="Переменные", course=self.course,
                                            video_url="https://youtube.com/watch?v=1")

    def test_crud(self):
        r = self.client.get("/lessons/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 1)

        r = self.client.post("/lessons/create/", {
            "title": "Циклы", "description": "for и while", "video_url": "https://youtube.com/watch?v=2",
            "course": self.course.pk, "preview": make_image("lesson.png"),
        }, format="multipart")
        self.assertEqual(r.status_code, 201, r.json())
        lesson_id = r.json()["id"]

        r = self.client.get(f"/lessons/{lesson_id}/")
        self.assertEqual(r.json()["course"], self.course.pk)

        r = self.client.patch(f"/lessons/{lesson_id}/update/", {"title": "Циклы и условия"})
        self.assertEqual(r.json()["title"], "Циклы и условия")
        r = self.client.put(f"/lessons/{lesson_id}/update/",
                            {"title": "Циклы", "course": self.course.pk, "video_url": ""})
        self.assertEqual(r.status_code, 200, r.json())

        r = self.client.delete(f"/lessons/{lesson_id}/delete/")
        self.assertEqual(r.status_code, 204)
        self.assertEqual(self.client.get(f"/lessons/{lesson_id}/").status_code, 404)

    def test_validation(self):
        r = self.client.post("/lessons/create/", {"title": "Без курса", "video_url": "не ссылка"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("course", r.json())
        self.assertIn("video_url", r.json())

    def test_lessons_deleted_with_course(self):
        self.client.delete(f"/courses/{self.course.pk}/")
        self.assertFalse(Lesson.objects.exists())
