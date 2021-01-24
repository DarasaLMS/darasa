from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from timezone_field.rest_framework import TimeZoneSerializerField
from apps.schools.models import Level, Student, Teacher, School
from ..models import User


class AccountsMiniSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "logo", "moto", "footer_text"]


class MiniLevelSerializer(serializers.ModelSerializer):
    school = AccountsMiniSchoolSerializer(many=False, read_only=True)

    class Meta:
        model = Level
        fields = ["id", "name", "school"]


class MiniStudentSerializer(serializers.ModelSerializer):
    level = MiniLevelSerializer(many=False, read_only=True)

    class Meta:
        model = Student
        fields = ["level"]


class MiniTeacherSerializer(serializers.ModelSerializer):
    school = AccountsMiniSchoolSerializer(many=False, read_only=True)

    class Meta:
        model = Teacher
        fields = ["position", "bio", "school"]


class UserSerializer(serializers.ModelSerializer):
    student = MiniStudentSerializer(many=False, read_only=True)
    teacher = MiniTeacherSerializer(many=False, read_only=True)
    timezone = TimeZoneSerializerField()

    class Meta:
        model = User
        fields = (
            "id",
            "title",
            "first_name",
            "last_name",
            "nickname",
            "gender",
            "email",
            "email_verified",
            "password",
            "phone",
            "picture",
            "role",
            "timezone",
            "calendar",
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
            "student",
            "teacher",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["title"] = ret["title"].title() if ret["title"] else ""
        ret["first_name"] = ret["first_name"].title() if ret["first_name"] else ""
        ret["last_name"] = ret["last_name"].title() if ret["last_name"] else ""
        return ret

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
    timezone = TimeZoneSerializerField()

    class Meta:
        model = User
        fields = (
            "id",
            "title",
            "first_name",
            "last_name",
            "nickname",
            "gender",
            "email",
            "phone",
            "picture",
            "role",
            "timezone",
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["title"] = ret["title"].title() if ret["title"] else ""
        ret["first_name"] = ret["first_name"].title() if ret["first_name"] else ""
        ret["last_name"] = ret["last_name"].title() if ret["last_name"] else ""
        return ret


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["is_active"] = user.is_active
        token["role"] = user.role
        token["email_verified"] = user.email_verified

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
