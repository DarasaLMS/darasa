from django.conf import settings
from rest_framework import serializers
from apps.accounts.api.serializers import (
    StudentSerializer,
    TeacherSerializer,
)
from ..models import Course, Lesson, Post, Classroom, Request


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["name", "description", "notes", "course", "parent_lesson"]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["name", "description", "category", "course", "parent_post"]


class CourseClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = [
            "id",
            "name",
            "description",
            "room_id",
            "welcome_message",
            "logout_url",
            "start_date",
            "end_date",
            "duration",
            "date_created",
            "created_by",
            "date_modified",
            "modified_by",
        ]


class CourseSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(many=False)
    assistant_teachers = TeacherSerializer(many=True)
    students = StudentSerializer(many=True)
    lessons = LessonSerializer(many=True)
    posts = PostSerializer(many=True)
    classrooms = CourseClassroomSerializer(many=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "description",
            "cover",
            "teacher",
            "assistant_teachers",
            "students",
            "lessons",
            "posts",
            "classrooms",
            "date_created",
            "created_by",
            "date_modified",
            "modified_by",
        ]


class MiniCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name"]


class ClassroomSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)

    class Meta:
        model = Classroom
        fields = [
            "id",
            "name",
            "description",
            "course",
            "room_id",
            "welcome_message",
            "logout_url",
            "start_date",
            "end_date",
            "duration",
            "date_created",
            "created_by",
            "date_modified",
            "modified_by",
        ]


class MiniClassroomSerializer(serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)

    class Meta:
        model = Classroom
        fields = ["id", "name", "course", "room_id"]


class RequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(many=False, read_only=True)
    teacher = TeacherSerializer(many=False, read_only=True)
    classroom = ClassroomSerializer(many=False, read_only=True)

    class Meta:
        model = Request
        fields = [
            "id",
            "student",
            "teacher",
            "classroom",
            "status",
            "date_created",
            "created_by",
            "date_modified",
            "modified_by",
        ]
