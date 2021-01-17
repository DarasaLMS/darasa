from django.contrib import admin
from .models import (
    School,
    Level,
    Student,
    Teacher,
    Course,
    Lesson,
    Post,
    Classroom,
    Request,
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "logo",
        "phone",
        "email",
        "support_email",
        "enroll_mode",
        "allow_teacher_verification",
    )

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "name",
                    "moto",
                    "logo",
                    "phone",
                    "email",
                    "support_email",
                    "about",
                    "terms_and_privacy",
                    "enroll_mode",
                    "allow_teacher_verification",
                    "footer_text",
                ]
            },
        ),
    )

    def has_add_permission(self, request):
        """Disable add school functionality if school instance exists."""
        result = super().has_add_permission(request)
        if result and Student.objects.exists():
            result = False

        return result


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "level")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user", "position", "bio", "verified", "verification_file")


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    exclude = ["created_by", "modified_by"]


class PostInline(admin.TabularInline):
    model = Post
    extra = 1
    exclude = ["created_by", "modified_by"]


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
                    "levels",
                    "classroom_join_mode",
                )
            },
        ),
    )
    inlines = [LessonInline, PostInline]
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    model = Lesson
    list_display = ("name", "description", "course", "parent_lesson", "position")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "notes",
                    "course",
                    "parent_lesson",
                    "position",
                )
            },
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
        "room_id",
        "start_date",
        "end_date",
        "duration",
        "date_modified",
    )
    fieldsets = (
        (None, {"fields": ("name", "description", "course", "welcome_message")}),
    )
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    model = Request
    list_display = ("course", "student", "teacher", "status", "date_modified")
    fieldsets = ((None, {"fields": ("course", "student", "status")}),)
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]
