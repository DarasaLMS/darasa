from django.conf import settings
from rest_framework import serializers
from apps.accounts.api.serializers import (
    StudentSerializer,
    TeacherSerializer,
)
from ..models import Course, Classroom, Request


class CourseSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(many=False, read_only=True)
    assistant_teachers = TeacherSerializer(many=True, read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "description",
            "teacher",
            "assistant_teachers",
            "students",
            "feedback_set",
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
            "course",
            "meeting_id",
            "welcome_message",
            "logout_url",
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
        fields = ["id", "name", "course", "meeting_id"]


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
