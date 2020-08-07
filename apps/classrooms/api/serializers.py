from django.conf import settings
from rest_framework import serializers
from apps.accounts.api.serializers import TeacherSerializer, StudentSerializer
from ..models import Course, Classroom, Request


class CourseSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(many=False, read_only=True)
    assistant_teacher = TeacherSerializer(many=False, read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "description",
            "teacher",
            "assistant_teacher",
            "students",
            "feedback_set",
            "date_modified",
        ]


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
            "date_modified",
        ]


class RequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(many=False, read_only=True)
    teacher = TeacherSerializer(many=False, read_only=True)
    classroom = ClassroomSerializer(many=False, read_only=True)

    class Meta:
        model = Request
        fields = ["id", "student", "teacher", "classroom", "status", "date_modified"]
