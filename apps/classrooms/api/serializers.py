from django.conf import settings
from rest_framework import serializers
from apps.classrooms.models import Course, Topic, Classroom, Request
from apps.accounts.api.serializers import TeacherSerializer, StudentSerializer


class CourseSerializer(serializers.ModelSerializer):
    teachers = TeacherSerializer(read_only=True, many=True)
    topics = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = ["id", "title", "description", "teachers", "topics", "date_modified"]


class TopicSerializer(serializers.ModelSerializer):
    teachers = TeacherSerializer(many=True, read_only=True)
    course = CourseSerializer(many=False, read_only=True)

    class Meta:
        model = Topic
        fields = ["id", "title", "description", "teachers", "course", "date_modified"]


class ClassroomSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(many=False, read_only=True)
    students = StudentSerializer(many=True, read_only=True)
    course = CourseSerializer(many=False, read_only=True)
    topic = TopicSerializer(many=False, read_only=True)

    class Meta:
        model = Classroom
        fields = [
            "id",
            "name",
            "teacher",
            "students",
            "course",
            "topic",
            "meeting_id",
            "welcome_message",
            "logout_url",
            "repeats",
            "class_time",
            "start_date",
            "end_date",
            "duration",
            "feedback_set",
            "date_modified",
        ]


class RequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(many=False, read_only=True)
    teacher = TeacherSerializer(many=False, read_only=True)
    classroom = ClassroomSerializer(many=False, read_only=True)

    class Meta:
        model = Request
        fields = ["id", "student", "teacher", "classroom", "status", "date_modified"]
