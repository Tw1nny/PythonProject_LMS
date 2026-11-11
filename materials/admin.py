from django.contrib import admin

from materials.models import Course, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "video_url")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title", "description")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "course", "video_url")
    list_filter = ("course",)
    search_fields = ("title", "description")
