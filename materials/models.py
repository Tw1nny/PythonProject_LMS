"""
Модели учебных материалов.

- Course — курс: название, превью, описание.
- Lesson — урок: название, описание, превью, ссылка на видео.
  Урок принадлежит курсу (ForeignKey): в одном курсе много уроков.
"""

from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    preview = models.ImageField(upload_to="materials/courses/", blank=True, null=True, verbose_name="Превью")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    preview = models.ImageField(upload_to="materials/lessons/", blank=True, null=True, verbose_name="Превью")
    video_url = models.URLField(blank=True, verbose_name="Ссылка на видео")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["id"]

    def __str__(self):
        return self.title
