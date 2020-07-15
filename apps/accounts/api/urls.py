from django.urls import re_path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import LoginView


urlpatterns = [
    re_path(r"^login/", LoginView.as_view(), name="login_obtain_token"),
    re_path(
        r"^login/token-refresh/",
        TokenRefreshView.as_view(),
        name="login_token_refresh",
    ),
    re_path(
        r"^login/token-verify/",
        TokenVerifyView.as_view(),
        name="login_token_verify",
    ),
]
