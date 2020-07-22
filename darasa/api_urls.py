from django.conf import settings
from django.urls import include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    re_path(
        r"^accounts/",
        include(("apps.accounts.api.urls", "accounts-api"), namespace="accounts-api"),
    ),
    re_path(
        r"^classrooms/",
        include(
            ("apps.classrooms.api.urls", "classrooms-api"), namespace="classrooms-api"
        ),
    ),
    re_path(
        r"^feedback/",
        include(("apps.feedback.api.urls", "feedback-api"), namespace="feedback-api"),
    ),
    re_path(
        r"^payments/",
        include(("apps.payments.api.urls", "payments-api"), namespace="payments-api"),
    ),
]
