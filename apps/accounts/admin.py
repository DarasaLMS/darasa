from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.loader import render_to_string
from django.contrib.auth.models import Group
from apps.schools.models import Student, Teacher
from .models import User
from .forms import UserAddForm, UserChangeForm, GroupAdminForm


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
                    "title",
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
                    "title",
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
        return render_to_string("widgets/picture.html", {"picture": obj.picture})

    render_picture.short_description = "Picture"


admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ["permissions"]
