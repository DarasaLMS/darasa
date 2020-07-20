from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.loader import render_to_string
from .models import User, Student, Teacher
from .forms import UserAddForm, UserChangeForm


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
        "user_type",
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
                    "user_type",
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
                    "user_type",
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


class StudentAdmin(admin.ModelAdmin):
    list_display = ("user",)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user",)


admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
