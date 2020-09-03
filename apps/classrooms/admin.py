from django.contrib import admin
from .models import Course, Classroom, Request


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ("name", "description", "students_count", "date_modified")
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
                )
            },
        ),
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    model = Classroom
    list_display = ("name", "course", "meeting_id", "date_modified")
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
                    "duration",
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
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "course",
                    "student",
                    "status",
                )
            },
        ),
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]
