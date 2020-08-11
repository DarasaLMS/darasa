from django.urls import re_path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import (
    LoginView,
    UserLisCreateView,
    UserRetrieveView,
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
    re_path(r"^users/$", UserLisCreateView.as_view(), name="user_list_create_view"),
    re_path(
        r"^users/(?P<user_id>.+)/$",
        UserRetrieveView.as_view(),
        name="user_retrieve_view",
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
