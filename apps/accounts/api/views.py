from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions, permissions, status, filters, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from ..models import VerificationToken, User, PasswordResetToken, EducationalStage
from .serializers import (
    LoginSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
    EducationalStageSerializer,
)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class UserListView(ListAPIView):
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
            "email": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
            "role": openapi.Schema(type=openapi.TYPE_STRING),
            "accept_terms": openapi.Schema(type=openapi.TYPE_STRING),
            "certificate": openapi.Schema(type=openapi.TYPE_FILE),
            "title": openapi.Schema(type=openapi.TYPE_STRING),
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

    try:
        user, _ = User.objects.get_or_create(email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.password = password
        user.role = role
        user.accepted_terms = accept_terms == "true"
        user.certificate = certificate
        user.title = title
        user.save()
        return Response(UserSerializer(instance=user).data)

    except Exception as error:
        raise exceptions.APIException(error)


class UserRetrieveView(RetrieveAPIView):
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
def verify_email(request, **kwargs):
    token = request.data.get("token", None)
    if not token:
        raise exceptions.NotAcceptable(detail=_("Token not found!"))

    verification_token = get_object_or_404(VerificationToken, token=token)
    if verification_token.user.check_email_verification(verification_token.token):
        return Response({"success": True})

    return Response(
        {"error": _("Token not valid!")}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def resend_email_verification(request, **kwargs):
    sent = request.user.send_verification_email()
    if sent:
        return Response({"success": True})

    return Response(
        {"error": _("Email already verified!")}, status=status.HTTP_400_BAD_REQUEST
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
def password_reset_request(request, **kwargs):
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
def password_reset_verify(request, **kwargs):
    password = request.data.get("password", None)
    token = request.data.get("token", None)
    verification_token = get_object_or_404(PasswordResetToken, token=token)
    if not password:
        raise exceptions.ValidationError({"password": _("Password must be specified!")})
    else:
        user = verification_token.user
        user.set_password(password)
        user.save()
        # delete verification token after usage
        verification_token.delete()
        return Response({"success": True})


class EducationalStageViewset(viewsets.ModelViewSet):
    queryset = EducationalStage.objects.all()
    serializer_class = EducationalStageSerializer
    permission_classes = [permissions.IsAuthenticated]
