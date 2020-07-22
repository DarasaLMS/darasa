from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, ListCreateAPIView, DestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions, permissions, serializers, status
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.api.serializers import (
    LoginSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
)
from apps.accounts.models import VerificationToken, User, PasswordResetToken, Teacher


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class UserView(ListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"


class UploadVerificationView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "verification_file",
                openapi.IN_FORM,
                required=True,
                type=openapi.TYPE_FILE,
            )
        ]
    )
    def post(self, request, format=None):
        teacher = Teacher.objects.filter(user=request.user)
        if not teacher:
            raise exceptions.NotFound(_("Teacher not found!"))

        if teacher.verification_file:
            teacher.verification_file.delete()

        verification_file = request.FILES["verification_file"]
        teacher.verification_file.save(verification_file.name, verification_file)
        teacher.save()
        serializer = self.serializer_class(instance=request.user)
        return Response(serializer.data)


class DeleteVerificationView(DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        teacher = Teacher.objects.filter(user=request.user)
        if teacher:
            teacher.verification_file.delete()
            teacher.save()

        return Response(self.serializer_class(instance=request.user).data)


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"verification_token": openapi.Schema(type=openapi.TYPE_STRING),},
    ),
)
@api_view(["POST"])
def verify_email(request):
    verification_token = request.data.get("verification_token", None)
    if not verification_token:
        raise exceptions.NotAcceptable(detail=_("Token not found!"))

    token = get_object_or_404(VerificationToken, token=verification_token)
    if token.user.check_email_verification(token):
        return Response({"success": True})

    else:
        return Response(
            {"error": _("Token not valid!")}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def resend_email_verification(request):
    request.user.send_verification_email()
    return Response({"success": True})


@swagger_auto_schema(
    method="POST",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"email": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
)
@api_view(["POST"])
def password_reset_request(request):
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
            "verification_token": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(["POST"])
def password_reset_verify(request):
    password = request.data.get("password", None)
    verification_token = request.data.get("verification_token", None)
    token = get_object_or_404(PasswordResetToken, token=verification_token)
    if not password:
        raise exceptions.ValidationError({"password": _("Password must be specified!")})
    else:
        user = token.user
        user.set_password(password)
        user.save()
        # delete token after usage
        token.delete()
        return Response({"success": True})

