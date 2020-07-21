from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions, generics, permissions, serializers, status
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.api.serializers import (
    LoginSerializer,
    UserSerializer,
    CurrentUserSerializer,
    PasswordResetRequestSerializer,
)
from apps.accounts.models import VerificationToken, User, PasswordResetToken, Teacher


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    lookup_field = "id"


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CurrentUserSerializer


class CurrentUserView(ModelViewSet):
    serializer_class = CurrentUserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    permission_classes = [permissions.IsAuthenticated]


verification_file_parameter = openapi.Parameter(
    "verification_file", openapi.IN_FORM, required=True, type=openapi.TYPE_FILE
)


class UploadVerificationView(APIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    @swagger_auto_schema(manual_parameters=[verification_file_parameter])
    def post(self, request, format=None):
        teacher = Teacher.objects.filter(user=request.user)
        if teacher:
            teacher = teacher.get()
        else:
            raise exceptions.NotFound(_("Teacher not found!"))

        file = request.FILES["verification_file"]
        if teacher.verification_file:
            teacher.verification_file.delete()

        teacher.verification_file.save(file.name, file)
        teacher.save()
        serializer = self.serializer_class(instance=request.user)
        return Response(serializer.data)


class DeleteVerificationView(generics.GenericAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        teacher = Teacher.objects.filter(user=request.user)
        if teacher:
            teacher = teacher.get()
            teacher.verification_file.delete()
            teacher.save()

        return Response(self.serializer_class(instance=request.user).data)


@api_view(["POST"])
def verify_email(request, token):
    if not token:
        raise exceptions.NotAcceptable(detail=_("Token not found!"))

    verify_token = get_object_or_404(VerificationToken, token=token)
    if verify_token.user.check_email_verification(token):
        return Response({"success": True})

    else:
        return Response(
            {"error": _("Token not valid!")}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def resend_verification(request):
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
        properties={"password": openapi.Schema(type=openapi.TYPE_STRING)},
    ),
)
@api_view(["POST"])
def password_reset_verify(request, token):
    token = get_object_or_404(PasswordResetToken, token=token)
    password = request.data.get("password", None)
    if not password:
        raise exceptions.ValidationError({"email": _("Email must be specified!")})
    else:
        user = token.user
        user.set_password(password)
        user.save()
        # delete token after usage
        token.delete()
        return Response({"success": True})

