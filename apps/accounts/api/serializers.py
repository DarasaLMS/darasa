from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.accounts.models import User, Student, Teacher


class UserSerializer(serializers.ModelSerializer):
    """Serializes fields from/to the User model"""

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
