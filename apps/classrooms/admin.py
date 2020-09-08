from django.contrib import admin
from .models import Course, Lesson, Post, Classroom, Request


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = (
        "name",
        "description",
        "teacher",
        "students_count",
        "classroom_join_mode",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "cover",
                    "teacher",
                    "assistant_teachers",
                    "students",
                    "educational_stages",
                    "classroom_join_mode",
                )
            },
        ),
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    model = Lesson
    list_display = ("name", "description", "course", "parent_lesson")
    fieldsets = (
        (
            None,
            {"fields": ("name", "description", "notes", "course", "parent_lesson",)},
        ),
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ("name", "description", "category", "course", "parent_post")
    fieldsets = (
        (
            None,
            {"fields": ("name", "description", "category", "course", "parent_post")},
        ),
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    model = Classroom
    list_display = (
        "name",
        "course",
        "meeting_id",
        "start_date",
        "end_date",
        "duration",
        "date_modified",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "course",
                    "meeting_id",
                    "moderator_password",
                    "attendee_password",
                    "welcome_message",
                )
            },
        ),
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    model = Request
    list_display = ("course", "student", "teacher", "status", "date_modified")
    fieldsets = ((None, {"fields": ("course", "student", "status",)},),)
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]
