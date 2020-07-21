from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_base64.serializers import ModelSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from apps.accounts.models import User, Student, Teacher


class DynamicFieldsModelSerializer(ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"


class TeacherSerializer(DynamicFieldsModelSerializer):
    courses = serializers.ReadOnlyField()
    classrooms = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    feedback = serializers.ReadOnlyField()
    rating = serializers.ReadOnlyField()

    class Meta:
        model = Teacher
        fields = [
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


class CurrentUserSerializer(serializers.ModelSerializer):
    student = StudentSerializer(required=False, allow_null=True)
    teacher = TeacherSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "email",
            "email_verified",
            "phone",
            "picture",
            "user_type",
            "accepted_terms",
            "is_active",
            "date_joined",
            "last_login",
            "student",
            "teacher",
        ]
        read_only_fields = ["email_verified"]
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
                teacher, _ = teacher.objects.get_or_create(user=instance)
                if data.get("verification_file"):
                    teacher.verification_file = data.get("verification_file")

                teacher.save()

        return super(CurrentUserSerializer, self).update(instance, validated_data)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            if self.instance.email != value:
                raise serializers.ValidationError(
                    _("User with this mail already exists!")
                )
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serializes fields from/to the User model"""

    student = StudentSerializer()
    teacher = TeacherSerializer(
        fields=["bio", "courses", "classrooms", "duration", "feedback", "rating"]
    )

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "gender",
            "email",
            "email_verified",
            "phone",
            "picture",
            "user_type",
            "accepted_terms",
            "is_active",
            "date_joined",
            "last_login",
            "student",
            "teacher",
        )
        read_only_fields = ("date_joined", "last_login", "email_verified")


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["is_active"] = user.is_active

        student = Student.objects.filter(user=user)
        if student.exists():
            token["user_type"] = user.user_type

        teacher = Teacher.objects.filter(user=user)
        if teacher.exists():
            token["user_type"] = user.user_type

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
        user.send_reset_mail()
