from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    LoginView,
    CurrentUserView,
    UserCreateView,
    UserView,
    UploadVerificationView,
    verify_email,
    resend_verification,
    password_reset_request,
    password_reset_verify,
)


urlpatterns = [
    re_path(r"^login/", LoginView.as_view(), name="login_obtain_token"),
    re_path(
        r"^login/token-refresh/",
        TokenRefreshView.as_view(),
        name="login_token_refresh",
    ),
    re_path(
        r"^login/token-verify/", TokenVerifyView.as_view(), name="login_token_verify",
    ),
    path("users/<uuid:id>/", UserView.as_view(), name="user_view"),
    path(
        "current/",
        CurrentUserView.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="view_user",
    ),
    path("create/", UserCreateView.as_view(), name="create_user"),
    path("verify/<uuid:token>/", verify_email, name="email_verification"),
    path("resend_verification/", resend_verification, name="resend_email_verification"),
    path(
        "request-password-reset/", password_reset_request, name="request_password_reset"
    ),
    path("reset-password/<uuid:token>/", password_reset_verify, name="reset_password"),
]
