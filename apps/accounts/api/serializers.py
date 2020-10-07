from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import ValidationError
from ..models import User, Student, Teacher, EducationalStage, School


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"


class MiniSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ["id", "name", "logo", "color"]


class EducationalStageSerializer(serializers.ModelSerializer):
    school = MiniSchoolSerializer(many=False, read_only=True)

    class Meta:
        model = EducationalStage
        fields = ["id", "name", "description", "school"]


class MiniStudentSerializer(serializers.ModelSerializer):
    educational_stage = EducationalStageSerializer(many=False, read_only=True)

    class Meta:
        model = Student
        fields = ["educational_stage"]


class MiniTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ["bio"]


class UserSerializer(serializers.ModelSerializer):
    student = MiniStudentSerializer(many=False, read_only=True)
    teacher = MiniTeacherSerializer(many=False, read_only=True)

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
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["title"] = ret["title"].title()
        ret["first_name"] = ret["first_name"].title()
        ret["last_name"] = ret["last_name"].title()
        return ret


class StudentSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(many=False, read_only=True)
    educational_stage = EducationalStageSerializer(many=False, read_only=True)

    class Meta:
        model = Student
        fields = ["user", "educational_stage"]


class StudentPictureSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    picture_url = serializers.SerializerMethodField("get_picture_url")

    class Meta:
        model = Student
        fields = ["user", "educational_stage", "picture_url"]

    def get_picture_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.user.picture.url)


class TeacherSerializer(serializers.ModelSerializer):
    user = MiniUserSerializer(many=False, read_only=True)

    class Meta:
        model = Teacher
        fields = ["user", "bio", "verified", "verification_file"]
        read_only_fields = ["verified", "verification_file"]


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
