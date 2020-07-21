from django.contrib import admin
from .models import Course, Topic, Classroom, Request


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    model = Course
    list_display = ("title", "description", "date_modified")
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    model = Topic
    list_display = ("title", "description", "course", "date_modified")
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    model = Classroom
    list_display = ("name", "course", "topic", "meeting_id", "teacher", "date_modified")
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    model = Request
    list_display = ("classroom", "student", "teacher", "status", "date_modified")
    date_hierarchy = "date_modified"
    ordering = ["-date_modified"]
