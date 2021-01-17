from django.conf import settings
from rest_framework import serializers
from apps.timetable.api.serializers import EventSerializer
from apps.accounts.api.serializers import MiniUserSerializer
from ..models import (
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


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"


class MiniSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "logo", "moto", "footer_text"]


class LevelSerializer(serializers.ModelSerializer):
    school = MiniSchoolSerializer(many=False, read_only=True)

    class Meta:
        model = Level
        fields = ["id", "name", "description", "school"]


class StudentSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(many=False, read_only=True)
    level = LevelSerializer(many=False, read_only=True)

    class Meta:
        model = Student
        fields = ["user", "level"]


class StudentPictureSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    picture_url = serializers.SerializerMethodField("get_picture_url")

    class Meta:
        model = Student
        fields = ["user", "level", "picture_url"]

    def get_picture_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.user.picture.url)


class TeacherSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(many=False, read_only=True)

    class Meta:
        model = Teacher
        fields = ["user", "position", "bio", "school", "verified", "verification_file"]
        read_only_fields = ["verified", "verification_file"]


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class LessonSerializer(serializers.ModelSerializer):
    children_lessons = RecursiveField(many=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "description",
            "notes",
            "course",
            "parent_lesson",
            "position",
            "children_lessons",
        ]


class PostSerializer(serializers.ModelSerializer):
    children_posts = RecursiveField(many=True)
    created_by = serializers.StringRelatedField()
    modified_by = serializers.StringRelatedField()

    class Meta:
        model = Post
        fields = [
            "id",
            "name",
            "description",
            "category",
            "course",
            "parent_post",
            "children_posts",
            "date_created",
            "created_by",
            "date_modified",
            "modified_by",
        ]


class CourseClassroomSerializer(serializers.ModelSerializer):
    event = EventSerializer(many=False, required=False)
    created_by = serializers.StringRelatedField()
    modified_by = serializers.StringRelatedField()

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
            "event",
            "date_created",
            "created_by",
            "date_modified",
            "modified_by",
        ]


class CourseSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(many=False, required=True)
    assistant_teachers = TeacherSerializer(many=True, required=False)
    levels = LevelSerializer(many=True, required=False)
    students = StudentSerializer(many=True, required=False)
    lessons = LessonSerializer(many=True, required=False)
    posts = PostSerializer(many=True, required=False)
    classrooms = CourseClassroomSerializer(many=True, required=False)
    created_by = serializers.StringRelatedField()
    modified_by = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "description",
            "cover",
            "teacher",
            "assistant_teachers",
            "levels",
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
    created_by = serializers.StringRelatedField()
    modified_by = serializers.StringRelatedField()

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
    course = MiniCourseSerializer(many=False, required=False)
    student = StudentSerializer(many=False, required=False)
    teacher = TeacherSerializer(many=False, required=False)
    classrooms = ClassroomSerializer(many=False, required=False)
    created_by = serializers.StringRelatedField()
    modified_by = serializers.StringRelatedField()

    class Meta:
        model = Request
        fields = [
            "id",
            "course",
            "student",
            "teacher",
            "classrooms",
            "status",
            "date_created",
            "created_by",
            "date_modified",
            "modified_by",
        ]
