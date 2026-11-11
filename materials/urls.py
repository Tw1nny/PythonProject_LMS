from django.urls import path
from rest_framework.routers import DefaultRouter

from materials import views

app_name = "materials"

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/", views.LessonListAPIView.as_view(), name="lesson_list"),
    path("lessons/create/", views.LessonCreateAPIView.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/", views.LessonRetrieveAPIView.as_view(), name="lesson_detail"),
    path("lessons/<int:pk>/update/", views.LessonUpdateAPIView.as_view(), name="lesson_update"),
    path("lessons/<int:pk>/delete/", views.LessonDestroyAPIView.as_view(), name="lesson_delete"),
] + router.urls
