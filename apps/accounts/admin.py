from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.loader import render_to_string
from django.contrib.auth.models import Group
from .models import User, Student, Teacher, EducationalStage, School
from .forms import UserAddForm, UserChangeForm, SchoolAdminForm, GroupAdminForm


class StudentInline(admin.TabularInline):
    model = Student
    extra = 1


class TeacherInline(admin.TabularInline):
    model = Teacher
    extra = 1


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = UserAddForm
    form = UserChangeForm
    ordering = ["first_name"]
    search_fields = ("email", "first_name", "last_name", "nickname")

    list_display = (
        "email",
        "nickname",
        "first_name",
        "last_name",
        "render_picture",
        "phone",
        "role",
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
                    "role",
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
                    "role",
                    "is_staff",
                    "is_active",
                )
            },
        ),
        ("Login", {"fields": ["email", "password1", "password2"]}),
    )

    inlines = [StudentInline, TeacherInline]

    def render_picture(self, obj):
        return render_to_string("picture.html", {"picture": obj.picture})

    render_picture.short_description = "Picture"


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ["permissions"]


@admin.register(EducationalStage)
class EducationalStageAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "educational_stage")


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "verified", "verification_file")


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "logo",
        "color",
        "phone",
        "email",
        "enroll_mode",
        "allow_teacher_verification",
    )

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "name",
                    "logo",
                    "color",
                    "phone",
                    "email",
                    "enroll_mode",
                    "allow_teacher_verification",
                ]
            },
        ),
    )
    form = SchoolAdminForm

