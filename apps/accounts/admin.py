from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.loader import render_to_string
from .models import User, Student, Teacher
from .forms import UserAddForm, UserChangeForm


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = UserAddForm
    form = UserChangeForm
    ordering = ["date_joined"]

    list_display = (
        "email",
        "nickname",
        "first_name",
        "last_name",
        "render_picture",
        "phone",
        "is_student",
        "is_teacher",
        "is_staff",
        "is_active",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "nickname",
                    "phone",
                    "gender",
                    "picture",
                    "is_student",
                    "is_teacher",
                    "is_staff",
                    "is_active",
                )
            },
        ),
        ("Login", {"fields": ["email", "password"]}),
    )

    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "nickname",
                    "phone",
                    "gender",
                    "picture",
                    "is_student",
                    "is_teacher",
                    "is_staff",
                    "is_active",
                )
            },
        ),
        ("Login", {"fields": ["email", "password1", "password2"]}),
    )

    def render_picture(self, obj):
        return render_to_string("picture.html", {"picture": obj.picture})

    render_picture.short_description = "Picture"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user",)

