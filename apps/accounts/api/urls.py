from django.urls import re_path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    LoginView,
    UserView,
    UserDetailView,
    verify_email,
    resend_email_verification,
    password_reset_verify,
    password_reset_request,
)


urlpatterns = [
    re_path(r"^login/$", LoginView.as_view(), name="login_obtain_token"),
    re_path(
        r"^token/refresh/$", TokenRefreshView.as_view(), name="login_token_refresh",
    ),
    re_path(
        r"^token/verification/$", TokenVerifyView.as_view(), name="login_token_verify",
    ),
    re_path(r"^users/$", UserView.as_view(), name="user_view"),
    re_path(
        r"^users/(?P<user_id>.+)/$", UserDetailView.as_view(), name="user_detail_view"
    ),
    re_path(r"^email/verification/$", verify_email, name="email_verification",),
    re_path(
        r"^email/verification/resend/$",
        resend_email_verification,
        name="resend_email_verification",
    ),
    re_path(r"^password/reset/$", password_reset_verify, name="reset_password",),
    re_path(
        r"^password/reset/request/$",
        password_reset_request,
        name="request_password_reset",
    ),
]
