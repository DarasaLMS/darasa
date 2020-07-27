from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from ..models import User, Student, Teacher


class StudentSerializer(serializers.ModelSerializer):
    active_classes = serializers.ReadOnlyField()
    pending_requests = serializers.ReadOnlyField()
    approved_requests = serializers.ReadOnlyField()
    rejected_requests = serializers.ReadOnlyField()

    class Meta:
        model = Student
        fields = [
            "user",
            "active_classes",
            "pending_requests",
            "approved_requests",
            "rejected_requests",
        ]


class MiniStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["user"]


class TeacherSerializer(serializers.ModelSerializer):
    courses = serializers.ReadOnlyField()
    classrooms = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    feedback = serializers.ReadOnlyField()
    rating = serializers.ReadOnlyField()

    class Meta:
        model = Teacher
        fields = [
            "user",
            "verification_file",
            "verified",
            "bio",
            "courses",
            "classrooms",
            "duration",
            "feedback",
            "rating",
        ]
        read_only_fields = ["verified"]


class MiniTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ["user", "bio"]


class UserSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=False, allow_null=True)
    teacher = TeacherSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "nickname",
            "gender",
            "email",
            "email_verified",
            "phone",
            "picture",
            "accepted_terms",
            "role",
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
            "student",
            "teacher",
        )
        read_only_fields = (
            "email_verified",
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
        )
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        student = None
        teacher = None

        if "student" in validated_data:
            student = validated_data.pop("student")

        if "teacher" in validated_data:
            teacher = validated_data.pop("teacher")

        # Create user, then set student and teacher if exists
        instance = User.objects.create_user(**validated_data)
        if student:
            Student.objects.update_or_create(user=instance, **student)

        if teacher:
            teacher, _ = Teacher.objects.get_or_create(user=instance)
            teacher.verification_file = teacher.get("verification_file")
            teacher.save()

        return instance

    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)

        if "student" in validated_data:
            data = validated_data.pop("student")
            if not data:
                Student.objects.filter(user=instance).delete()
            else:
                Student.objects.update_or_create(user=instance, defaults=data)

        if "teacher" in validated_data:
            data = validated_data.pop("teacher")
            if not data:
                Teacher.objects.filter(user=instance).delete()
            else:
                teacher, _ = Teacher.objects.get_or_create(user=instance)
                if data.get("verification_file"):
                    teacher.verification_file = data.get("verification_file")

                teacher.save()

        return super(UserSerializer, self).update(instance, validated_data)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            if self.instance.email != value:
                raise serializers.ValidationError(
                    _("User with this mail already exists!")
                )

        return value


class MiniUserSerializer(serializers.ModelSerializer):
    student = MiniStudentSerializer(required=False, allow_null=True)
    teacher = MiniTeacherSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "nickname",
            "gender",
            "email",
            "phone",
            "picture",
            "role",
            "is_staff",
            "is_active",
            "student",
            "teacher",
        )
        read_only_fields = ("is_staff", "is_active")


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["is_active"] = user.is_active

        student = Student.objects.filter(user=user)
        if student.exists():
            token["role"] = user.role

        teacher = Teacher.objects.filter(user=user)
        if teacher.exists():
            token["role"] = user.role

        return token


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = get_user_model().objects.filter(email=value)
        if user.exists():
            return value
        else:
            raise serializers.ValidationError(_("No user found with this email!"))

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        user.send_password_reset_email()
