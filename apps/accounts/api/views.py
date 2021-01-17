from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions, permissions, status, filters, viewsets, generics
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from apps.schools.models import School, Level
from ..models import User, VerificationToken, PasswordResetToken
from .serializers import LoginSerializer, UserSerializer, PasswordResetRequestSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["first_name", "last_name", "nickname", "email", "phone"]
    filterset_fields = ["is_staff", "is_active", "role"]
    ordering = ["first_name"]


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "first_name": openapi.Schema(type=openapi.TYPE_STRING),
            "last_name": openapi.Schema(type=openapi.TYPE_STRING),
            "title": openapi.Schema(type=openapi.TYPE_STRING),
            "email": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
            "role": openapi.Schema(type=openapi.TYPE_STRING),
            "accept_terms": openapi.Schema(type=openapi.TYPE_STRING),
            "certificate": openapi.Schema(type=openapi.TYPE_FILE),
        },
    ),
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_user_view(request, *args, **kwargs):
    first_name = request.data.get("first_name", None)
    last_name = request.data.get("last_name", None)
    title = request.data.get("title", "")
    email = request.data.get("email", None)
    password = request.data.get("password", None)
    role = request.data.get("role", None)
    accept_terms = request.data.get("accept_terms", False)
    certificate = request.data.get("certificate", None)
    level_id = request.data.get("level", None)

    try:
        if not email:
            return Response(
                "User must have an email", status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                "User account already exists!", status=status.HTTP_409_CONFLICT
            )

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            title=title,
            role=role,
            accepted_terms=accept_terms == "true",
        )

        user.set_password(password)

        if role == "student":
            user.student.level = Level.objects.filter(id=level_id).first()
            user.student.save()

        if role == "teacher":
            user.teacher.school = School.objects.first()
            user.teacher.verification_file = certificate
            user.teacher.save()

        user.save()
        return Response(UserSerializer(instance=user).data)

    except Exception as error:
        raise exceptions.APIException(error)


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "user_id"


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"token": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def verify_account(request, **kwargs):
    token = request.data.get("token", None)
    if not token:
        raise exceptions.NotAcceptable(detail=_("Token not found!"))

    verification_token = generics.get_object_or_404(VerificationToken, token=token)
    if verification_token.user.check_email_verification(verification_token.token):
        verification_token.user.is_active = True
        verification_token.user.save()
        return Response(UserSerializer(instance=verification_token.user).data)

    return Response(
        {"error": _("Token not valid!")}, status=status.HTTP_400_BAD_REQUEST
    )


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"email": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def request_password_reset(request, **kwargs):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

    return Response({"success": True})


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "password": openapi.Schema(type=openapi.TYPE_STRING),
            "token": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request, **kwargs):
    password = request.data.get("password", None)
    token = request.data.get("token", None)
    verification_token = generics.get_object_or_404(PasswordResetToken, token=token)
    if not password:
        raise exceptions.ValidationError({"password": _("Password must be specified!")})

    user = verification_token.user
    user.set_password(password)
    user.save()
    # delete verification token after usage
    verification_token.delete()
    return Response({"success": True})
