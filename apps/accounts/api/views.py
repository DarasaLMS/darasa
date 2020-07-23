from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, ListCreateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions, permissions, status
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.api.serializers import (
    LoginSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
)
from apps.accounts.models import VerificationToken, User, PasswordResetToken


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class UserView(ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"token": openapi.Schema(type=openapi.TYPE_STRING),},
    ),
)
@api_view(["POST"])
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

